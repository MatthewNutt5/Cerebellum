"""
TestConfig.py
This file contains the TestConfig class, which is used to specify the conditions
of a test - power supply voltages/currents, Tamalero programs, etc.
Configurations can be stored in JSON files for later use. Primarily used by
runTest.py.

This file also contains the CriterionConfig class, which is a helper class used
to specify an individual criterion the test should evaluate.
TODO: types of criterion: current, voltage, DAQ transient, Tamalero script
"""

from json import dump, load



class TestConfig:

    def __init__(self):

        self.LVPSVoltage    = 0.0       # If CV, set voltage to this; if CC, this is voltage limit
        self.LVPSCurrent    = 0.0       # If CV, this is current limit; if CC, set current to this
        self.LVPSConstCurr  = False     # Will the LVPS run in CC mode? (False = CV)
        self.HVPSEnable     = False     # Enable HVPS operation?
        self.HVPSVoltage    = 0.0       # "
        self.HVPSCurrent    = 0.0       # "
        self.HVPSConstCurr  = False     # "
        self.auxPSUSettings = []        # Ditto the above, as ordered triples [Voltage, Current, CC]
        
        self.tempEnable     = False     # Check for RTD temp before starting test?
        self.maxTemp        = -30.0     # RTD must measure below this temp (Celsius) before starting test

        self.criteria       = []        # List of CriterionConfig objects

    

    """
    Writes the contents of the object to the given filepath in the JSON format. 
    """
    def writeJSON(self, filepath):

        # Convert all objects to dicts
        vars_dict = vars(self).copy()
        vars_dict["criteria"] = []
        for criterion in self.criteria:
            vars_dict["criteria"].append(vars(criterion))
        
        # Open file and write JSON
        with open(filepath, 'w') as f:
            dump(vars_dict, f, indent=4)



    """
    Reads the given filepath for a JSON representation of a configuration;
    populates the fields of the object with the values.
    """
    def readJSON(self, filepath):
        
        # Open file and read JSON
        with open(filepath, 'r') as f:
            self.__dict__ = load(f)

        # Convert object dicts to objects
        for index, criterion in enumerate(self.criteria):
            self.criteria[index] = CriterionConfig(criterion["criterionType"], vars_dict=criterion)



class CriterionConfig:

    def __init__(self, criterionType, vars_dict={}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            
            self.criterionType = criterionType

            match criterionType:

                case "PSUCurrent":
                    self.ineq       = "<"   # The measured current must be > or < than...
                    self.PSUCurrent = 0.0   # ... this current

                case "PSUVoltage":
                    self.ineq       = "<"   # The measured voltage must be > or < than...
                    self.PSUVoltage = 0.0   # ... this voltage

                case _:
                    raise ValueError("Invalid criterionType value")
