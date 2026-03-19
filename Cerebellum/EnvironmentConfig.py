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

# Always make sure that Cerebellum and its submodules are on the import path
import sys, os
ABS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ABS_DIR)                # Cerebellum modules
sys.path.append(f"{ABS_DIR}/../")       # Cerebellum parent directory
sys.path.append(f"{ABS_DIR}/Device/")   # Device submodule
from Cerebellum.Device.Device import DeviceConfig

from json import dump, load
import importlib, logging
logging.basicConfig(level=logging.INFO)



class EnvironmentConfig:

    def __init__(self):
        self.device_config_list: list[DeviceConfig] = [] # List of DeviceConfig objects to be constructed into device_list

    """
    Writes the contents of the object to the given filepath in the JSON format. 
    """
    def write_json(self, filepath: str) -> None:

        # Convert all objects to dicts
        json_dict = vars(self).copy()
        json_dict["device_config_list"] = [vars(config) for config in self.device_config_list]

        # Add identifier
        json_dict["type"] = "EnvironmentConfig"
        
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
        identifier = json_dict["type"]
        if (identifier != "EnvironmentConfig"):
            raise ValueError(f"Invalid EnvironmentConfig JSON file (type field is {identifier}, not EnvironmentConfig).")
        
        # Assign fields to JSON data
        # Convert object dicts to objects
        self.device_config_list.clear()
        for config in json_dict["device_config_list"]:
            
            # Look for config type field to inform what sort of PowerSupplyConfig to construct
            config_type = config["type"]

            # From the config type, find the module name, and import the config constructor from the module
            # E.g. config["type"] = SCPIPowerSupplyConfig --> module_name = SCPIPowerSupply, and use config_type as the constructor
            module_name = config_type.replace("Config", "")
            if (module_name == config_type):
                raise TypeError(f"Config type ({config_type}) does not have \"Config\" in its name; cannot produce module name.")
            try:
                module = importlib.import_module(f"Cerebellum.Device.{module_name}")
                constructor = getattr(module, config_type)
                self.device_config_list.append(constructor(vars_dict=config))
            except Exception as e:
                logging.warning(f"Generated DeviceConfig module/constructor name (Cerebellum.Device.{module_name}.{config_type}) is invalid: {e}")
                logging.warning(f"Skipping config...")
