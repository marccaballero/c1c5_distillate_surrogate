# Import Section

import dist_traycol_cost
import json
from json import JSONEncoder

class TrayColumn:

    def __init__(self, feed, number_trays, feed_tray, reflux_ratio, df_ratio, tray_spacing, material, weld_eff):
        # ID
        self.col_id = None

        # Design variables
        self.feed = feed
        self.op_pressure = feed.pressure
        self.number_trays = number_trays
        self.feed_tray = feed_tray
        self.reflux_ratio = reflux_ratio
        self.df_ratio = df_ratio
        self.tray_spacing = tray_spacing
        self.material = material
        self.weld_eff = weld_eff

        # Convergence
        self.convergence = None

        # Gathered attributes
        self.q_reb = None
        self.t_reb = None
        self.q_cond = None
        self.t_cond = None
        self.boilup_vol_rate = None
        self.max_vap_rate = None
        self.min_vap_dens = None
        self.max_liq_dens = None

        # Calculated attributes
        self.a_reb = None
        self.a_cond = None
        self.cond_type = None
        self.reb_utility = None
        self.cond_utility = None
        self.col_diam = None
        self.col_length = None
        self.wall_thickness = None
        self.col_shell_mass = None

        # Costs
        self.column_cost = None
        self.reb_cost = None
        self.cond_cost = None
        self.tray_cost = None
        self.equipment_cost = None
        self.fcop = None
        self.ut_cost = None
        self.tac = None

        # Output streams
        self.dist_stream = None
        self.bot_stream = None
    
    def add_input_data(self, path):
 
        # ToDo: Provided a path, populate the attributes that are input data and calculates the possible calculatable attributes. First need to explore the data structure of ASPEN (or a custom one). Maybe it can be implemented in the init
        pass
    
    def calculate_cost(self, cepci, c_sf, interest_rate, amort_time):
        # ToDo: add docstrings
        self.reb_cost = dist_traycol_cost.individual_equipment_cost("Heat Exchanger",
                                                                    "U-tube Kettle reboiler",
                                                                    self.a_reb,
                                                                    self.material)

        if self.cond_type == "Air cooler":
            self.cond_cost = dist_traycol_cost.individual_equipment_cost("Heat Exchanger",
                                                                        "Packaged mechanical refrigerator",
                                                                        self.a_cond,
                                                                        self.material)
        else:
            self.cond_cost = dist_traycol_cost.individual_equipment_cost("Heat Exchanger",
                                                                        "U-tube Kettle reboiler",
                                                                        self.a_cond,
                                                                        self.material)

        self.tray_cost = dist_traycol_cost.individual_equipment_cost("Distillation column",
                                                                     "Sieve tray",
                                                                     self.col_diam,
                                                                     self.material)
        self.column_cost = dist_traycol_cost.individual_equipment_cost("Distillation column",
                                                                    "Vertical pressure vessel",
                                                                    self.col_shell_mass,
                                                                    self.material)

        self.equipment_cost = self.reb_cost + self.cond_cost + self.number_trays*self.tray_cost + self.column_cost

        self.ut_cost = dist_traycol_cost.utility_cost(self.q_reb, self.t_reb, self.q_cond, self.t_cond, cepci, c_sf)

        self.total_cost = dist_traycol_cost.accr(interest_rate, amort_time)*self.equipment_cost + self.ut_cost
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        # return json.dumps(self, default=lambda o: o.__dict__)

class material_stream:
  
    def __init__(self, streamname:str, comp_list:list = [], mass_flows:list = [], temperature:float = 273, pressure:float = 1000):
        self.streamname = streamname.upper()
        self.streamtype = "MATERIAL"
        self.comp_list = comp_list
        self.mass_flows = mass_flows
        self.temperature = temperature
        self.pressure = pressure
