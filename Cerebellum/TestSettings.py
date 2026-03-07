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



class Event:
    def __init__(self):
        self.type = ""

class SetPSUEvent(Event):
    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            self.type           = "SetPSUEvent"         # Object type (only used for JSON read/write)
            self.PSUidx         = 0                     # Index of the PSU (correlate with PSUConfigList in EnvironmentConfig)
            self.channel        = 0                     # PSU channel to impart these settings
            self.enable         = True                  # Is this power supply channel enabled for this test?
            self.voltage        = 0.0                   # Voltage setting
            self.current        = 0.0                   # Current setting

class EvalPSUVoltageEvent(Event):
    def __init__(self, vars_dict={}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            self.type           = "EvalPSUVoltageEvent" # Object type
            self.PSUidx         = 0                     # Index of the PSU
            self.channel        = 0                     # PSU channel to measure
            self.VoltageLow     = 0.0                   # The measured voltage must be >= this voltage
            self.VoltageHigh    = float('inf')          # The measured voltage must be <= this voltage

class EvalPSUCurrentEvent(Event):
    def __init__(self, vars_dict={}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            self.type           = "EvalPSUCurrentEvent" # Object type
            self.PSUidx         = 0                     # Index of the PSU
            self.channel        = 0                     # PSU channel to measure
            self.CurrentLow     = 0.0                   # The measured current must be >= this current
            self.CurrentHigh    = float('inf')          # The measured current must be <= this current

class EvalPSUPowerEvent(Event):
    def __init__(self, vars_dict={}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            self.type           = "EvalPSUPowerEvent"   # Object type
            self.PSUidx         = 0                     # Index of the PSU
            self.channel        = 0                     # PSU channel to measure
            self.PowerLow       = 0.0                   # The measured power must be >= this power
            self.PowerHigh      = float('inf')          # The measured power must be <= this power



class TestSettings:

    PSUSettingsList : list[SetPSUEvent]
    eventList       : list[Event]

    def __init__(self):
        
        self.PSUSettingsList    = []    # List of SetPSUEvent objects
        self.eventList          = []    # List of Event objects

    """
    Writes the contents of the object to the given filepath in the JSON format. 
    """
    def writeJSON(self, filepath: str):

        # Convert all objects to dicts
        json_dict = vars(self).copy()
        json_dict["PSUSettingsList"] = [vars(event) for event in self.PSUSettingsList]
        json_dict["eventList"] = [vars(event) for event in self.eventList]

        # Add identifier
        json_dict["type"] = "TestSettings"
        
        # Open file and write JSON
        with open(filepath, 'w') as f:
            dump(json_dict, f, indent=4)

    """
    Reads the given filepath for a JSON representation of a configuration;
    populates the fields of the object with the values.
    """
    def readJSON(self, filepath: str):
        
        # Open file and read JSON
        with open(filepath, 'r') as f:
            json_dict = load(f)
        
        # Check for identifier
        if ("type" not in json_dict):
            raise KeyError(f"Invalid TestSettings JSON file (no \"type\" field found).")
        identifier = json_dict["type"]
        if (identifier != "TestSettings"):
            raise ValueError(f"Invalid TestSettings JSON file (\"type\" field is {identifier}).")
        
        # Assign fields to JSON data

        # Convert object dicts to objects
        self.PSUSettingsList.clear()
        for event in json_dict["PSUSettingsList"]:
            self.PSUSettingsList.append(SetPSUEvent(vars_dict=event))

        self.eventList.clear()
        for event in json_dict["eventList"]:
            if (event["type"] == "SetPSUEvent"):
                self.eventList.append(SetPSUEvent(vars_dict=event))
            elif (event["type"] == "EvalPSUVoltageEvent"):
                self.eventList.append(EvalPSUVoltageEvent(vars_dict=event))
            elif (event["type"] == "EvalPSUCurrentEvent"):
                self.eventList.append(EvalPSUCurrentEvent(vars_dict=event))
            elif (event["type"] == "EvalPSUPowerEvent"):
                self.eventList.append(EvalPSUPowerEvent(vars_dict=event))
