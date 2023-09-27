""" Constants for the cost of different equipments. 
Aranged in dictionaries with the corresponding categories

Retrieved from Ray Sinnot & Gavin Towler, Chemical Engineering Design (Sixth Edition)

Constants for equation 6.15, from table 6.6.
Installation factors, from table 6.3
Material factors, from table 6.5

Correlation of type Cost_e = IF * MF * (a+b*S**n)

"""
installation_factors = {"Compressor":             2.5,
                        "Distillation column":    4, 
                        "Fired heater":           2,
                        "Heat exchanger":         3.5,
                        "Instrument":             4,
                        "Miscellaneous":          2.5,
                        "Pressure vessel":        4,
                        "Pump":                   4
                        }

material_factors = {"Carbon steel":               1.0,
                    #"Aluminium":                  1.07,
                    #"Bronze":                     1.07,
                    "Cast steel":                 1.1,
                    "304 stainless steel":        1.3,
                    "316 stainless steel":        1.3,
                    "321 stainless steel":        1.5,
                    "Hastelloy C":                1.55,
                    "Monel":                      1.65,
                    #"Nickel":                     1.7,
                    "Inconel":                    1.7
                    }
# ToDo: Aluminium, bronze and Nickel discarded due to lack of data for maximum stress. Update in a future

#                              Equipment type                       a       b       n
equipment_cost_correlations = {"U-tube Kettle reboiler":          [25000,    340,   0.9],
                              "Sieve tray":                       [110,      380,   1.8],
                              "Vertical pressure vessel":         [10000,     29,  0.85],
                              "Packaged mechanical refrigerator": [21000,   3100,   0.9]
                              }

"""Material properties section
"""

material_density = {"Carbon steel":               7750,
                    #"Aluminium":                  1.07,
                    #"Bronze":                     1.07,
                    "Cast steel":                 7750,
                    "304 stainless steel":        8030,
                    "316 stainless steel":        8030,
                    "321 stainless steel":        8030,
                    "Hastelloy C":                8500,
                    "Monel":                      8860,
                    #"Nickel":                     1.7,
                    "Inconel":                    8410
                    }

# Material densities in kg/m3. Retrieved from: ASME BVPC Code Sec. II D.2 (2010 Version). In kg/m3

max_stress_ASME_BPV = {
                      # "Temperature": [40, 65 ,100, 125, 150, 200, 250, 300, 325, 350, 375, 400, 425, 450, 475],

                      "Temperature": [313, 338, 373, 398, 423, 473, 523, 573, 598, 623, 648, 673, 698, 723, 748],


                       "Carbon steel": [118, 118, 118, 118, 118, 118, 114, 107, 104, 101, 97.8, 89.1, 75.4, 62.6, 45.5],

                       "Cast steel": [118, 118, 118, 118, 118, 118, 114, 107, 104, 101, 97.8, 89.1, 75.4, 62.6, 45.5],

                       "304 stainless steel": [115, 115, 115, 115, 115, 110, 103, 97.7, 95.7, 94.1, 92.6, 91.3, 90.0, 88.7, 86.6],

                       "316 stainless steel":  [115, 115, 115, 115, 115, 109, 103, 98, 95.7, 94.1, 92.8, 90.9, 89.0, 87.8, 86.6],

                       "Hastelloy C": [690, 690, 690, 690, 690, 690, 690, 636, 631, 626, 621, 615, 609, 602, 595],

                       "Monel": [115, 107, 99.4, 95.9, 93.7, 91.1, 90.4, 90.3, 90.3, 90.2, 89.5, 89.5, 88.9, 78.5, 60.8],

                       "Inconel": [158, 152, 146, 144, 143, 142, 140, 138, 137, 136, 135, 134, 132, 130, 118]
                       }

# Note on stresses for materials: Extracted from ASME BPV Code Sec. II D.1 (2010 version). Many different alloys can be referred to a "general" type of material such as Stainless steel (for example). Details of the specific alloy are commented below. Values in MPa.

# Carbon steel: Carbon steel for Forgings, Spec No. SA-266, Type/Grade 1, Alloy designation K03506. Line number 19 of table 1A pages 10-13.

# Cast steel: Carbon steel for Castings, Spec No. SA-266, Type/Grade 1, Alloy designation K03506. Line number 18 of table 1A pages 10-12.

# 304 stainless steel: 18Cr-8Ni for Forgings, Spec No. SA-965, Type/Grade F304L, Alloy designation S30403. Line number 13 of table 1A pages 82-84.

# 316 stainless steel: 16Cr-12Ni-2Mo for Forgings, Spec No. SA-965, Type/Grade F316L, Alloy designation S31603. Line number 21 of table 1A pages 66-68.

# Hastelloy C: 59Ni-23Cr-16Mo-1.6Cu for Forgings, Spec No. SB-462, Type/Grade -, Alloy designation N06200, Line number 34 of Table 1B pages 516 - 517

# Monel: 67Ni-30Cu for Forgings, Spec No. SB-564, Type/Grade -, Alloy designation N04400, Line number 29 of table 1B pages 194-196

# Inconel: 72Ni-15Cr-8Fe for Forgings, Spec No. SB-564, Type-Grade -, Alloy designation N06600, Line number 42 of table 1B pages 210-212

utility_fluids = {# Fluid                    Mode     Tin[K] HTC[W/m2K]  ARH [K]  ARL[K] Dtm[K]   Type HX
                  "HP Steam Generation":  ["cooling",   522,    6000,      3273,    532.5,  10,  "Shell & Tube"],
                  "MP Steam Generation":  ["cooling",   447,    6000,     532.5,    457.5,  10,  "Shell & Tube"],
                  "LP Steam Generation":  ["cooling",   397,    6000,     457.5,    407.5,  10,  "Shell & Tube"],
                  "Air":                  ["cooling",   303,     111,     407.5,    317.5,  10,    "Air Cooler"],
                  "Cooling Water":        ["cooling",   293,    3750,     317.5,    302.5,   5,  "Shell & Tube"],
                  "Rf1":                  ["cooling",   248,    1300,     302.5,    251.5,   3,  "Shell & Tube"],
                  "Rf2":                  ["cooling",   233,    1300,     251.5,    236.5,   3,  "Shell & Tube"],
                  "Rf3":                  ["cooling",   208,    1300,     236.5,    210.5,   2,  "Shell & Tube"],
                  "Rf4":                  ["cooling",   170,    1300,     210.5,      173,   2,  "Shell & Tube"],
                  
                  "Rf4 Generation":       ["heating",   171,    1300,     169.5,        0,   2, "Shell & Tube"],
                  "Rf3 Generation":       ["heating",   209,    1300,     207.5,    169.5,   2, "Shell & Tube"],
                  "Rf2 Generation":       ["heating",   234,    1300,     231.5,    207.5,   3, "Shell & Tube"],
                  "Rf1 Generation":       ["heating",   249,    1300,     246.5,    231.5,   3, "Shell & Tube"],
                  "LP Steam":             ["heating",   398,    6000,     388.5,    246.5,  10, "Shell & Tube"],
                  "MP Steam":             ["heating",   448,    6000,     438.5,    388.5,  10, "Shell & Tube"],
                  "HP Steam":             ["heating",   523,    6000,     513.5,    438.5,  10, "Shell & Tube"],
                  "Hot Oil":              ["heating",   553,   232.3,     548.5,    513.5,   5, "Shell & Tube"],
                  }
# Utility fluid properties and values retrieved from Aspen HYSYS Process Utility Manager.