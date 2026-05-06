"""
EnvironmentConfig.py
This file contains the EnvironmentConfig class, which is used to specify
the control structure of a given test stand - IP addresses, interface types,
etc. Ideally, the environment configuration is determined once and will not
change between test cycles. Configurations can be stored in JSON files for
later use. Primarily used by EnvironmentControl.

This file also contains the PSUConfig class, which is a helper class used
to specify the control configuration of a power supply in the test environment.
"""

# Prevents TypeError on type hints for Python 3.7 to 3.9
from __future__ import annotations

from Cerebellum.Common import DEVICE_CONFIGS
from Cerebellum.Device.Device import DeviceConfig

from json import dump, load
import logging



class EnvironmentConfig:

    def __init__(self):

        self.device_config_list : list[DeviceConfig]    = []        # List of DeviceConfig objects to be constructed into device_list
        self.python_path        : str                   = "python3" # Python path or alias to use for calling the test subprocess
        self.shutdown_order     : list[int]             = []        # List of Device indices specifying the shutdown order upon test termination

    """
    Writes the contents of the object to the given filepath in the JSON format. 
    """
    def write_json(self, filepath: str) -> None:

        # Convert all objects to dicts, add identifiers to each
        json_dict = vars(self).copy()
        json_dict["device_config_list"] = []
        for config in self.device_config_list:
            config_dict = vars(config)
            config_dict["class_name"] = config.__class__.__name__
            json_dict["device_config_list"].append(config_dict)

        # Add identifier for the JSON itself
        json_dict["class_name"] = self.__class__.__name__
        
        # Open file and write JSON
        with open(filepath, 'w') as f:
            dump(json_dict, f, indent=4)

    """
    Reads the given filepath for a JSON representation of a configuration;
    populates the fields of the object with the values.
    """
    def read_json(self, filepath: str) -> None:
        
        # Open file and read JSON
        with open(filepath, 'r') as f:
            json_dict = load(f)

        # Check for identifier
        json_class_name = json_dict.pop("class_name")
        if (json_class_name != self.__class__.__name__):
            raise ValueError(f"Invalid {self.__class__.__name__} JSON file: class_name field is {json_class_name}, not {self.__class__.__name__}.")
        
        # Assign fields to JSON data
        self.python_path = json_dict["python_path"]
        self.shutdown_order = json_dict["shutdown_order"]

        # Convert object dicts to objects
        self.device_config_list.clear()
        for config in json_dict["device_config_list"]:
            
            # Look for config class_name field to inform what sort of Config to construct
            # Also remove class_name from the dict so it doesn't end up in the instance
            config_class_name = str(config.pop("class_name"))
            device_class_name = config_class_name.replace("Config", "")
            
            # Use the corresponding constructor from DEVICE_CONFIGS
            if (device_class_name in DEVICE_CONFIGS):
                constructor = DEVICE_CONFIGS[device_class_name]
                try:
                    self.device_config_list.append(constructor(vars_dict=config))
                except Exception as e:
                    logging.warning(f"DeviceConfig constructor {config_class_name}() failed: {e}")
                    logging.warning("Skipping config...")
            else:
                logging.warning(f"DeviceConfig constructor {config_class_name}() not in DEVICE_CONFIGS constructor list. Either the {device_class_name} module isn't installed, or the constructor previously failed to verify.")
                logging.warning("Skipping config...")
