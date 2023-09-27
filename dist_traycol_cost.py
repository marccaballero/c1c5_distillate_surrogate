"""Module with the cost functions for a distillation column (+-30% estimation)
Retrieved from  Chapter 6 of Ray Sinnot & Gavin Towler, Chemical Engineering Design (Sixth Edition)
"""

# Import Section
from cost_factors_constants import *
import numpy as np
# Fixed variables definitions

# CEPCI = 802.6 # For 2023. Check source
# C_SF = 4.5  # (from example in Ulrich and Vasudevan, check for an updated prize of fuel)
# INTEREST_RATE = 0.2
# AMORT_TIME = 5.0 # In years
# TRAY_SPACING = 0.6 # Typical tray spacing. Detailed tray spacing calculation is iterative to minimize cost. Simplified.
# WELD_EFFICIENCY = 1 # Assumption. For detailed coefficient consult ASME BPV Code Sec. VIII D.1 Part UW

def tpc_traycol(eq_cost, ut_cost, accr_f):



    fcop = eq_cost*accr_f

    tpc = fcop + ut_cost
    return tpc


def estimated_equipment_cost(a_reb, a_cond, q_cond ,cond_type, col_diam, shell_m, number_trays, material):
    """Calculates the cost of the equipment of a distillation column (tower, trays, condenser and reboiler), based on equation 6.15 of Ray Sinnot & Gavin Towler, Chemical Engineering Design (Sixth Edition)

    Args:
        a_reb (float): area of the reboiler [m2]
        a_cond (float): area of the condenser [m2]
        col_diam (float): column diameter [m]
        shell_m (float): column mass shell [kg]
        number_trays (float): number of trays in column [-]
        material (str): material which the equipment is made of.
        Available options: "Carbon steel", "Cast steel", 
        "304 stainless steel", "316 stainless steel", "321 stainless steel",
        "Hastelloy C", "Monel", "Inconel". (Aluminium, bronze and nickel removed due to 
        unavailability of data for maximum tensile strength for pressure vessels (ASME BPVC))

    Returns:
        float: cost of the equipment in $
    """
    c_reb = individual_equipment_cost("Heat Exchanger",
                                     "U-tube Kettle reboiler",
                                     a_reb,
                                     material)
    # ToDo: Include air cooled condenser
    if cond_type == "Air Cooler":
        c_cond = individual_equipment_cost("Heat Exchanger",
                                      "Packaged mechanical refrigerator",
                                      q_cond,
                                      material)
    else:
        c_cond = individual_equipment_cost("Heat Exchanger",
                                      "U-tube Kettle reboiler",
                                      a_cond,
                                      material)
    c_tray = individual_equipment_cost("Distillation column",
                                      "Sieve tray",
                                      col_diam,
                                      material)
    c_column = individual_equipment_cost("Distillation column",
                                        "Vertical pressure vessel",
                                        shell_m,
                                        material)

    column_equipment_cost = c_reb + c_cond + c_tray*number_trays + c_column
    return column_equipment_cost


def utility_cost(q_reb, t_reb, q_cond, t_cond, cepci, c_sf):
    """Calculates the cost of the hot and cold utilities (reboiler and condenser) of a distillation 
    column.
      Equations from:
      Gael D. Ulrich and Palligarnai T. Vasudevan, How to Estimate Utility Costs, 
      Chem Eng. pp. 66-69, April 2006
      https://terpconnect.umd.edu/~nsw/chbe446/HowToEstimateUtilityCosts-UlrichVasudevan2006.pdf

    Args:
        Q_reb (float): Reboiler duty in kW
        T_reb (float): Reboiler temperature in K
        Q_cond (float): Condenser duty in kW
        T_cond (float): Condenser temperature in K
        CEPCI (float): Chemical Engineering Plant Cost Index
        C_sf (float): Cost of fuel in $/GJ (based on assumption that electricity 
        is generated by burning some fuel)

    Returns:
        Float: Cost of hot and cold utilities (reboiler and condenser) of a 
        distillation column, in $/year
    """
    #ToDo: Create an updated version with better correlations. Ask Qing
    
    # Correlation for hot utility cost, expressed in $/kJ of heating capacity.
    # Overestimation. If proess steam is available, cost correlation is different, but steam mass is required.
    # ToDo: Consider changing it in a future if an "easy" way is found to calculate the mass of steam
    c_hu = 7e-7 * np.abs(q_reb) ** (-0.9) * t_reb**0.5 * cepci + 6e-8 * t_reb**0.5 * c_sf

    # Correlation for cold utility cost, expressed in $/kJ of heating capacity
    # Overestimation. If cooling water is available, cost correlation is diferent, but cooling water mass is required.
    # If air cooler is the condenser, the correlation should be one for electricity cost (to power the fans)
    # ToDo: Consider changing it in a future if an "easy" way is found to calculate the mass of steam
    c_cu = 0.6 * np.abs(q_cond) ** (-0.9) * t_cond ** (-3) * cepci + 1.1e+6 * t_cond**-5 * c_sf

    dist_ut_cost = (c_cu * np.abs(q_reb) + c_hu * np.abs(q_cond)) * 3600*24*300
    #Multiplication by sec/year based on duty units (kW)
    return dist_ut_cost


def accr(interest, n_years):
    """Calculates the Annual Capital Charge Ratio (ACCR) to convert the capital cost into a future 
    annual capital charge (comparing the magnitude of a capital investment with a revenue stream 
    in the future).
    
    Equation 6.47 from Ray Sinnot & Gavin Towler, Chemical Engineering Design (Sixth Edition)
    
    The annual capital charge ratio is the fraction of the principal that must be paid out each year 
    to fully repay the principal and all accumulated interest over the life of the investment. This 
    is the same formula used for calculating payments on home mortgages and other loans where the 
    principal is amortized over the loan period.

    Args:
        interest (float): (compound) interest rate
        n_years (float): expected years of plant amortization

    Returns:
        Float: value of the ACCR
    """

    # Annual capital charge ratio "ACCR"
    ACCR = (interest * (1 + interest) ** n_years) / ((1 + interest) ** n_years - 1)

    return ACCR

def individual_equipment_cost(equipment_category, equipment_type, s, material):
    """ Calculates the estimate cost for a given equipment.
    Formula: Cost_e = IF * MF * (a+b*s**n)
    Equation 6.15 with constants from table 6.6 Retrieved from
    Ray Sinnot & Gavin Towler, Chemical Engineering Design (Sixth Edition)
    with Installation factor(s) from table 6.3 and Material factor(s) from table 6.5

    Args:
        equipment_category (str): general category of equipment. Available options: "Compressor", 
        "Distillation column", "Fired heater", "Heat exchanger", "Instrument", 
        "Miscellaneous", "Pressure vessel" and "Pump".
        
        equipment_type (str): specific type of equipment. Available options: 
        "U-tube Kettle reboiler, "Sieve tray", "Vertical pressure vessel" and 
        "Packaged mechanical refrigerator".
        
        s (size parameter): characteristic size parameter of the equipment 
        (example: heat exchanger area, column diameter, shell mass...)
        
        material (str): material which the equipment is made of.
        Available options: "Carbon steel", "Cast steel", 
        "304 stainless steel", "316 stainless steel", "321 stainless steel",
        "Hastelloy C", "Monel", "Inconel". (Aluminium, bronze and nickel removed due to 
        unavailability of data for maximum tensile strength for pressure vessels (ASME BPVC))

    Returns:
        Float: calculated estimated cost (in $)
    """
    mat_factor = material_factors[material]
    inst_factor = installation_factors[equipment_category]
    a = equipment_cost_correlations[equipment_type][0]
    b = equipment_cost_correlations[equipment_type][1]
    n = equipment_cost_correlations[equipment_type][2]

    c = inst_factor*mat_factor*(a+b*s**n)
    return c

def col_diameter (vap_rate, vap_density, liq_density, tray_spacing):
    """Calculates an estimate for the diameter of a distillation column.
    Equations 11.47 and 11.48 retrieved from
    Ray Sinnot & Gavin Towler, Chemical Engineering Design (Sixth Edition)

    Args:
        vap_rate (float): maximum vapour flowrate through the column [kg/h]
        vap_density (float): maximum liquid density in column [kg/m3]
        liq_density (float): minimum vapour density in column [kg/m3]
        tray_spacing (float): tray spacing for column [m]
        
    Returns:
        float: estimation for column diameter in [m]
    """
    u_v = (-0.171*tray_spacing**2 + 0.27*tray_spacing - 0.047)*((liq_density - vap_density)/vap_density)**0.5

    d_c = np.sqrt(4*vap_rate/(np.pi*vap_density*u_v))
    return d_c

def col_wall_thickness (op_pressure, col_diam, weld_efficiency, max_allow_stress):
    """Calculates the wall thickness of a distillation column.
    Equation 13.41 retrieved from
    Ray Sinnot & Gavin Towler, Chemical Engineering Design (Sixth Edition)

    Args:
        op_pressure (float): operating pressure of the distillation column [Pa]
        
        col_diam (float): column diameter [m]
        
        weld_efficiency (float): Welded joint efficiency. [-] Unitless ranging from 0 to 1.

        max_allow_stress (float): maximum allowed stress associated to the construction material. [Pa]

    Returns:
        float: value of the calculated wall thickness, in m
    """
    design_pressure = op_pressure*1.1

    t_w = design_pressure*col_diam/(2*max_allow_stress*weld_efficiency-1.2*design_pressure)
    return t_w

def max_stress (material, temperature):
    """Finds the max stress for a material at a given temperature

    Args:
        material (str): material which the equipment is made of.
        Available options: "Carbon steel", "Cast steel", 
        "304 stainless steel", "316 stainless steel", "321 stainless steel",
        "Hastelloy C", "Monel", "Inconel". (Aluminium, bronze and nickel removed due to 
        unavailability of data for maximum tensile strength for pressure vessels (ASME BPVC))
        
        temperature (float): design temperature [K]

    Returns:
        float: value of the max stress allowable from the ASME BPVC tables, transformed to Pa
    """

    idx=0
    for i in max_stress_ASME_BPV["Temperature"]:
        if i < temperature:
            idx+=1
        else: break

    if temperature not in max_stress_ASME_BPV["Temperature"]:
        idx = idx-1

    m_stress = max_stress_ASME_BPV[material][idx]
    return float(m_stress*1000000)


def col_length(n_trays, tray_spacing, vol_boilup_rate, col_d):
    """ Calculates an estimation for the column length.
    
    For sump height uses an estimation of being a cylinder with a flat head with a residence time of
    7 minutes, based on Table 4.1 from Kister's Distillation Operation, with minimum 0.5 meters.
    
    For overhead and feed stages, a fixed height is set, based on industrial experience

    Args:
        n_trays (int): number of trays [-]
        tray_spacing (float): distance between trays [m]
        vol_boilup_rate (float): boilup volumetric flowrate [m3/s]
        col_d (float): column diameter [m]

    Returns:
        float: value of an estimation for the colum lentgh [m]
    """
    overhead_height = 1 # Educated guess based on industrial experience
    
    extra_height = 0.5 # Educated guess based on industrial experience (for feed distributor)
    
    tau = 7*60 # Residence time, 7 minutes according to Table 4.1 in Kister, Distillation Operation
    h_sump = tau*vol_boilup_rate/(np.pi/4*col_d**2)
    sump_height = max(0.5, h_sump)
    
    l_c = n_trays*tray_spacing + sump_height + overhead_height + extra_height
    return l_c


def column_shell_mass (col_d, col_l, wall_thickness, material):
    """ Calculates the metal mass of the shell of a distillation column.
    
    Retrieved from example 6.2 from
    Ray Sinnot & Gavin Towler, Chemical Engineering Design (Sixth Edition) 

    Args:
        col_d (float): column diameter [m]
        col_l (float): column length [m]
        wall_thickness (float): column wall thickness [m]
        material (str): material which the equipment is made of.
        Available options: "Carbon steel", "Cast steel", 
        "304 stainless steel", "316 stainless steel", "321 stainless steel",
        "Hastelloy C", "Monel", "Inconel". (Aluminium, bronze and nickel removed due to 
        unavailability of data for maximum tensile strength for pressure vessels (ASME BPVC))

    Returns:
        float: value for the metal mass of the shell of a distillation column [kg]
    """

    mat_dens = material_density[material]
    s_m = np.pi*col_d*col_l*wall_thickness*mat_dens
    return s_m

def hx_dist_area(t_op, duty, mode):
    """Suggests the type and area required for a reboiler or condenser,
    given the process fluid operating temperature and duty required.

    Args:
        t_op (float): Process fluid inlet temperature [K]
        duty (float): duty required to boil/condense the fluid [W]
        mode (str): cooling or heating required for the process fluid

    Returns:
        area (float):  estimation of the required area for the HX [m2]
        ut_fluid (str): utility fluid required
        type_hx (str): type of the hx required
    """
    key = None
    for i in utility_fluids.items():
        if i[1][4]<t_op<i[1][3] and i[1][0]==mode:
            key = i[0]
    if key:
        area = np.abs(duty)/(utility_fluids[key][2]*np.abs(t_op-utility_fluids[key][1]))
        type_hx = utility_fluids[key][-1]
        ut_fluid = key
    else:
        area = 1e+16
        ut_fluid = "Out of bounds"
        type_hx = "Shell & Tube"

    return area, ut_fluid, type_hx