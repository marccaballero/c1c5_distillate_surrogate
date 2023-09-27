import timeit
import random
import re
import glob
import os
import latin_hypercube
import numpy as np
from tqdm import tqdm
from AspenPlusLink import Simulation
from dist_class import material_stream, TrayColumn

# For reproducibility
random.seed(42)
np.random.seed(42)

# Fixed parameters
FEED_PRES = 2.5e+6

TRAY_SPACING = 0.6
MATERIAL = "304 stainless steel"
WELD_EFF = 1.0
INTEREST = 0.2
PLANT_LIFE = 5
CEPCI = 802.6
C_SF = 4.5

COMPONENT_LIST = ["METHA-01",
                    "ETHAN-01",
                    "ETHYL-01",
                    "PROPA-01",
                    "PROPY-01",
                    "N-BUT-01",
                    "N-PEN-01",
                    "BENZE-01",
                    ]

# Data ranges for LHS
PRESS_B = [1e+5, 5.5e+6] # Pa
TEMP_B = [73, 400] # K
NT_B = [2,220]
FT_B = [0.05, 0.95]
RR_B = [0.1, 50]
DF_B = [0.01, 0.99]
COMP_B = [0, 5] # kg/s

N_SAMPLES = int(1e5)

# Latin Hypercube
lhs_ub = [PRESS_B[0], TEMP_B[0], NT_B[0], FT_B[0], RR_B[0], DF_B[0], COMP_B[0], COMP_B[0], COMP_B[0], COMP_B[0],COMP_B[0],COMP_B[0],COMP_B[0],COMP_B[0]]
lhs_lb = [PRESS_B[-1], TEMP_B[-1], NT_B[-1], FT_B[-1], RR_B[-1], DF_B[-1],  COMP_B[-1], COMP_B[-1], COMP_B[-1], COMP_B[-1],COMP_B[-1],COMP_B[-1],COMP_B[-1],COMP_B[-1]]
int_vars = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

p = latin_hypercube.normalized(len(lhs_ub), N_SAMPLES)
samples = latin_hypercube.sampling(lhs_lb, lhs_ub, p)
samples = latin_hypercube.int_vars(int_vars, samples)

# Start the simulation
sim = Simulation(AspenFileName="Base_case.bkp", WorkingDirectoryPath= r"./Simulation_Files/sim_data", VISIBILITY=False)
# Change working directory to parent folder
os.chdir('../')
# Set flow basis to mass
sim.AspenSimulation.Tree.Elements("Data").Elements("Setup").Elements("Global").Elements("Input").Elements("BASIS").Value = "MASS"
# Initialize the feed stream
INLET_STREAM = material_stream("FEED")
# Add the feed stream
sim.StreamPlace(Streamname=INLET_STREAM.streamname, Streamtype= INLET_STREAM.streamtype)
# Add the column
sim.BlockPlace(Blockname="COL", EquipmentType="Radfrac")
# Create empty streams for the RadFrac out
sim.StreamPlace(Streamname="DIST", Streamtype= "MATERIAL")
sim.StreamPlace(Streamname="BOT", Streamtype= "MATERIAL")
# Connect the streams to the column
sim.StreamConnect(Blockname="COL", Streamname=INLET_STREAM.streamname, Portname="F(IN)")
sim.StreamConnect(Blockname="COL", Streamname="DIST", Portname="LD(OUT)")
sim.StreamConnect(Blockname="COL", Streamname="BOT", Portname="B(OUT)")

q = 0
nc = 0
q0 = 0
databatch =[]
pbar = tqdm(total=N_SAMPLES)
start = timeit.default_timer()

# Safeguard for re-starting in case code crashed.
dir_path = r'.\disc_data\*.json'
l = glob.glob(dir_path)
last_l = [l[i].split('\\')[-1] for i in range(len(l))]
q = max([int(re.findall(r'\d+', p)[0]) for p in last_l],default=0)

if q>0:
    q+=1
    samples = samples[q:]
    pbar.update(q)
    q0 = q

for sample in samples:

    INLET_STREAM.comp_list = COMPONENT_LIST
    INLET_STREAM.mass_flows = sample[-8:].tolist()
    INLET_STREAM.pressure = sample[0]
    INLET_STREAM.temperature = sample[1]
    ft = round(sample[3]*sample[2])
    ft = 1 if ft<=0 else sample[2] if ft>sample[2] else ft # Check that FT is in bounds

    COL = TrayColumn(INLET_STREAM,
                    sample[2], # NT
                    ft, # FT
                    sample[4], # RR
                    sample[5], # DFR
                    TRAY_SPACING,
                    MATERIAL,
                    WELD_EFF)
    COL.col_id = q
    

    # Set the feed stream
    sim.STRM_Set_Pressure(Streamname=INLET_STREAM.streamname, Pressure=INLET_STREAM.pressure)
    sim.STRM_Set_Temperature(Streamname=INLET_STREAM.streamname, Temp=INLET_STREAM.temperature)

    for i in range(len(INLET_STREAM.comp_list)):
        sim.STRM_Set_ComponentFlowRate(Streamname=INLET_STREAM.streamname,
                                      ComponentFlowRate=INLET_STREAM.mass_flows[i],
                                      Compoundname=INLET_STREAM.comp_list[i])

    # Column specs
    # NStages
    sim.BLK.Elements("COL").Elements("Input").Elements("NSTAGE").Value = COL.number_trays
    # Condenser Type
    sim.BLK.Elements("COL").Elements("Input").Elements("CONDENSER").Value = "TOTAL"
    # Distillate to feed ratio
    sim.BLK.Elements("COL").Elements("Input").Elements("D:F").Value = COL.df_ratio
    # Reflux ratio
    sim.BLK.Elements("COL").Elements("Input").Elements("BASIS_RR").Value = COL.reflux_ratio
    # Feed stage
    sim.BLK.Elements("COL").Elements("Input").Elements("FEED_STAGE").Elements("FEED").Value = COL.feed_tray
    # Pressure
    sim.BLK.Elements("COL").Elements("Input").Elements("PRES1").Value = COL.feed.pressure

    # Run the simulation
    sim.EngineRun()

    # Check for convergence errors (?)
    COL.convergence = sim.BLK.Elements("COL").Elements("Output").Elements("BLKSTAT").Value
    # 0 = Converged
    # other values = Not converged or converged with errors
    if COL.convergence !=0:
        nc+=1

    databatch.append(COL)

    # Restart sim
    sim.EngineReinit()

    # Save every 1% of iterations
    if ((q+1)%(N_SAMPLES/100)==0 or (q==N_SAMPLES-1)):
        with open('./disc_data/disc_sims_{index}.json'.format(index = q), 'w') as fp:
            # Loop through the batch of data and write each element as a line in the json,
            for datapoint in databatch:
                jsonstr = datapoint.toJSON()
                fp.write(jsonstr)
                fp.write("\n")
        # Then, reset the batch
        databatch =[]    
    q += 1
    pbar.update()
sim.CloseAspen()

end = timeit.default_timer()
pbar.close()
generation_time = end - start

script_log_name = './disc_data/disc_sampling_log.txt'
if not os.path.isfile(script_log_name):
    with open(script_log_name, 'w') as fp:
        fp.write('{total} distillations simulated'.format(total=N_SAMPLES-q0))
        fp.write("\n")
        
        fp.write('{unc} unconverged simulations'.format(unc=nc))
        fp.write("\n")
        
        fp.write('Data generation time =  %.2f seconds' % ((end - start)))
        fp.write("\n")

print('Finish!')
