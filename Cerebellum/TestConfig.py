"""
TestConfig.py
This file contains the TestConfig class, which is used to specify the
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
ABS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ABS_DIR)                # Cerebellum modules
sys.path.append(f"{ABS_DIR}/../")       # Cerebellum parent directory
sys.path.append(f"{ABS_DIR}/Device/")   # Device submodule
from Cerebellum.Event import *
EVT_MOD = sys.modules["Cerebellum.Event"]

from json import dump, load
import logging
logging.basicConfig(level=logging.INFO)



class TestConfig:

    def __init__(self):

        self.event_list     : list[Event]   = []    # List of Event objects to be executed during the test
        self.shutdown_order : list[int]     = []    # List of Device indices specifying the shutdown order for PSUs

    """
    Writes the contents of the object to the given filepath in the JSON format. 
    """
    def write_json(self, filepath: str):

        # Convert all objects to dicts, add identifiers to each
        json_dict = vars(self).copy()
        json_dict["event_list"] = []
        for event in self.event_list:
            event_dict = vars(event)
            event_dict["class_name"] = event.__class__.__name__
            json_dict["event_list"].append(event_dict)

        # Add identifier for the JSON itself
        json_dict["class_name"] = self.__class__.__name__
        
        # Open file and write JSON
        with open(filepath, 'w') as f:
            dump(json_dict, f, indent=4)

    """
    Reads the given filepath for a JSON representation of a configuration;
    populates the fields of the object with the values.
    """
    def read_json(self, filepath: str):
        
        # Open file and read JSON
        with open(filepath, 'r') as f:
            json_dict = load(f)
        
        # Check for identifier
        json_class_name = json_dict.pop("class_name")
        if (json_class_name != self.__class__.__name__):
            raise ValueError(f"Invalid {self.__class__.__name__} JSON file (class_name field is {json_class_name}, not {self.__class__.__name__}).")
        
        # Assign fields to JSON data
        # Convert object dicts to objects
        self.event_list.clear()
        for event in json_dict["event_list"]:

            # Look for event class_name field to inform what sort of Event to construct
            # Also remove class_name from the dict so it doesn't end up in the instance
            event_class_name = event.pop("class_name")

            # From the event class_name, import its constructor from the Event module
            try:
                constructor = getattr(EVT_MOD, event_class_name)
                self.event_list.append(constructor(vars_dict=event))
            except Exception as e:
                logging.warning(f"Invalid Event class_name ({event_class_name}) found during JSON read: {e}")
                logging.warning(f"Skipping event...")
