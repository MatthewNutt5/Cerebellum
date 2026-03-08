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
    type            : str

class SetPSUEvent(Event):

    PSUidx          : int   # Index of the PSU (correlate with PSUConfigList in EnvironmentConfig)
    channel         : int   # PSU channel to impart these settings
    enable          : bool  # Should the power supply be enabled or disabled?
    voltage         : float # Voltage setting
    current         : float # Current setting

    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            self.type           = "SetPSUEvent"
            self.PSUidx         = 0
            self.channel        = 0
            self.enable         = True
            self.voltage        = 0.0
            self.current        = 0.0

class EvalPSUVoltageEvent(Event):

    PSUidx          : int   # Index of the PSU
    channel         : int   # PSU channel to measure
    VoltageLow      : float # The measured voltage must be >= this voltage
    VoltageHigh     : float # The measured voltage must be <= this voltage

    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            self.type           = "EvalPSUVoltageEvent"
            self.PSUidx         = 0
            self.channel        = 0
            self.VoltageLow     = 0.0
            self.VoltageHigh    = float('inf')

class EvalPSUCurrentEvent(Event):

    PSUidx          : int   # Index of the PSU
    channel         : int   # PSU channel to measure
    CurrentLow      : float # The measured current must be >= this current
    CurrentHigh     : float # The measured current must be <= this current

    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            self.type           = "EvalPSUCurrentEvent"
            self.PSUidx         = 0
            self.channel        = 0
            self.CurrentLow     = 0.0
            self.CurrentHigh    = float('inf')

class EvalPSUPowerEvent(Event):

    PSUidx          : int   # Index of the PSU
    channel         : int   # PSU channel to measure
    PowerLow        : float # The measured power must be >= this power
    PowerHigh       : float # The measured power must be <= this power

    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            self.type           = "EvalPSUPowerEvent"
            self.PSUidx         = 0
            self.channel        = 0
            self.PowerLow       = 0.0
            self.PowerHigh      = float('inf')



class TestSettings:

    PSUSettingsList : list[SetPSUEvent] # List of SetPSUEvent objects
    eventList       : list[Event]       # List of Event objects

    def __init__(self):
        
        self.PSUSettingsList    = []
        self.eventList          = []

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
