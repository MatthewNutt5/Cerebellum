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
        vars_dict["eventList"] = [vars(event) for event in self.eventList]
        
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

        for index, event in enumerate(self.eventList):
            if (event.type == "EvalVoltageEvent"):
                self.eventList[index] = EvalVoltageEvent(vars_dict=event)
            elif (event.type == "EvalCurrentEvent"):
                self.eventList[index] = EvalCurrentEvent(vars_dict=event)



class PSUSettings:
    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            self.PSUidx     = 0         # Index of the PSU (correlate with PSUConfigList in EnvironmentConfig)
            self.channel    = 0         # PSU channel to impart these settings
            self.enable     = True      # Is this power supply channel enabled for this test?
            self.voltage    = 0.0       # Voltage setting
            self.current    = 0.0       # Current setting



class Event:
    def __init__(self):
        self.type = ""

class EvalVoltageEvent(Event):
    def __init__(self, vars_dict={}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            self.type           = "EvalVoltageEvent"    # Object type (only used for JSON read/write)
            self.PSUidx         = 0                     # Index of the PSU
            self.channel        = 0                     # PSU channel to measure
            self.VoltageLow     = 0.0                   # The measured voltage must be >= this voltage
            self.VoltageHigh    = float('inf')          # The measured voltage must be <= this voltage

class EvalCurrentEvent(Event):
    def __init__(self, vars_dict={}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            self.type           = "EvalCurrentEvent"    # Object type (only used for JSON read/write)
            self.PSUidx         = 0                     # Index of the PSU
            self.channel        = 0                     # PSU channel to measure
            self.CurrentLow     = 0.0                   # The measured current must be >= this current
            self.CurrentHigh    = float('inf')          # The measured current must be <= this current
