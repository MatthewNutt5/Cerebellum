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
"""

from json import dump, load



class TestSettings:

    def __init__(self):
        
        self.PSUSettingsList    = []    # List of PSUSettings objects
        self.eventList          = []    # List of Event objects

    """
    Writes the contents of the object to the given filepath in the JSON format. 
    """
    def writeJSON(self, filepath: str):

        # Convert all objects to dicts
        vars_dict = vars(self).copy()
        vars_dict["PSUSettingsList"] = [vars(PSU) for PSU in self.PSUSettingsList]
        #vars_dict["criteriaList"] = [vars(criterion) for criterion in self.criteriaList]
        
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

        # for index, criterion in enumerate(self.criteriaList):
            # self.criteriaList[index] = Criterion(criterion["criterionType"], vars_dict=criterion)



class PSUSettings:

    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            self.enable     = True      # Is this power supply enabled for this test?
            self.voltage    = 0.0       # Voltage setting
            self.current    = 0.0       # Current setting



class Event:
    pass

class PSUVoltageEvent(Event):
    def __init__(self, eventType, vars_dict={}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            self.type = "PSUVoltageEvent"       # Object type (only used for JSON read/write)
            self.PSUidx         = 0             # Index of the PSU (0 = LVPS, 1 = HVPS, 2+ = Aux PSUs)
            self.PSUVoltageLow  = 0.0           # The measured voltage must be <= this voltage
            self.PSUVoltageHigh = float('inf')  # The measured voltage must be <= this voltage

class PSUCurrentEvent(Event):
    def __init__(self, eventType, vars_dict={}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            self.type = "PSUCurrentEvent"       # Object type (only used for JSON read/write)
            self.PSUidx         = 0             # Index of the PSU (0 = LVPS, 1 = HVPS, 2+ = Aux PSUs)
            self.PSUCurrentLow  = 0.0           # The measured current must be <= this current
            self.PSUCurrentHigh = float('inf')  # The measured current must be <= this current
