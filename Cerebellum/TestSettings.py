"""
TestSettings.py
This file contains the TestSettings class, which is used to specify the
conditions of a test - power supply voltages/currents, Tamalero programs, etc.
Settings can be stored in JSON files for later use. Primarily used by
EnvironmentControl.

This file also contains the PSUSettings class, which is a helper class used to
specify the settings of a power supply used during a test, and the Criterion
class, which is a helper class used to specify an individual criterion the test
should evaluate.
TODO: types of criterion: current, voltage, DAQ transient, Tamalero script
"""

from json import dump, load



class TestSettings:

    def __init__(self):
        
        self.tempEnable         = False             # Check for RTD temp before starting test?
        self.maxTemp            = -30.0             # RTD must measure below this temp (Celsius) before starting test
        self.PSUSettingsList    = []                # List of PSUSettings objects
        self.PSUSettingsList.append(PSUSettings())  # First PSU; LVPS
        self.PSUSettingsList.append(PSUSettings())  # Second PSU; HVPS
        self.criteriaList       = []                # List of Criterion objects

    """
    Writes the contents of the object to the given filepath in the JSON format. 
    """
    def writeJSON(self, filepath: str):

        # Convert all objects to dicts
        vars_dict = vars(self).copy()
        vars_dict["PSUSettingsList"] = [vars(PSU) for PSU in self.PSUSettingsList]
        vars_dict["criteriaList"] = [vars(criterion) for criterion in self.criteriaList]
        
        # Open file and write JSON
        with open(filepath, 'w') as f:
            dump(vars_dict, f, indent=4)

    """
    Reads the given filepath for a JSON representation of a configuration;
    populates the fields of the object with the values.
    """
    def readJSON(self, filepath: str):
        
        # Open file and read JSON
        with open(filepath, 'r') as f:
            self.__dict__ = load(f)

        # Convert object dicts to objects
        for index, PSU in enumerate(self.PSUSettingsList):
            self.PSUSettingsList[index] = PSUSettings(vars_dict=PSU)

        for index, criterion in enumerate(self.criteriaList):
            self.criteriaList[index] = Criterion(criterion["criterionType"], vars_dict=criterion)



class PSUSettings:

    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            self.enable     = True      # Is this power supply enabled for this test?
            self.constCurr  = False     # Will the LVPS run in CC mode? (False = CV)
            self.voltage    = 0.0       # If CV, set voltage to this; if CC, this is voltage limit
            self.current    = 0.0       # If CV, this is current limit; if CC, set current to this



class Criterion:

    def __init__(self, criterionType, vars_dict={}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            
            self.criterionType = criterionType

            # NOTE: Would use a match/case here, but that's only available with Python 3.10+
            if (criterionType == "PSUCurrent"):
                self.PSUidx     = 0     # Index of the PSU (0 = LVPS, 1 = HVPS, 2+ = Aux PSUs)
                self.ineq       = "<"   # The measured current must be > or < than...
                self.PSUCurrent = 0.0   # ... this current
            elif (criterionType == "PSUVoltage"):
                self.PSUidx     = 0     # Index of the PSU (0 = LVPS, 1 = HVPS, 2+ = Aux PSUs)
                self.ineq       = "<"   # The measured voltage must be > or < than...
                self.PSUVoltage = 0.0   # ... this voltage
            else:
                raise ValueError(f"Invalid criterionType value: {criterionType}")
