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

# Always make sure that Cerebellum and its submodules are on the import path
import sys, os
sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Cerebellum.Event import *

from json import dump, load



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
