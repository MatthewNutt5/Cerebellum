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

from json import dump, load



class PSUConfig:

    displayName     : str               # Display name of the power supply
    interface       : str               # Communication interface (SCPI / Custom)
    protocol        : str               # Communication protocol (IP / Serial)
    IP              : str               # IP address
    COM             : str               # COM port (e.g. /dev/ttyACM0, COM1)
    baudrate        : int               # COM baudrate
    implementation  : str               # Name of implementation (e.g. CAENPowerSupply)
    customConfig    : dict[str, str]    # Dict of config variables to be used by a custom implementation

    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            self.displayName    = "Power Supply"
            self.interface      = ""
            self.protocol       = ""
            self.IP             = ""
            self.COM            = ""
            self.baudrate       = 115200
            self.implementation = ""
            self.customConfig   = {}



class EnvironmentConfig:

    addressRB       : str               # Ethernet IP address of KCU
    PSUConfigList   : list[PSUConfig]   # List of PSUConfig objects

    def __init__(self):
        self.addressRB      = ""
        self.PSUConfigList  = []

    """
    Writes the contents of the object to the given filepath in the JSON format. 
    """
    def writeJSON(self, filepath: str) -> None:

        # Convert all objects to dicts
        json_dict = vars(self).copy()
        json_dict["PSUConfigList"] = [vars(config) for config in self.PSUConfigList]

        # Add identifier
        json_dict["type"] = "EnvironmentConfig"
        
        # Open file and write JSON
        with open(filepath, 'w') as f:
            dump(json_dict, f, indent=4)

    """
    Reads the given filepath for a JSON representation of a configuration;
    populates the fields of the object with the values.
    """
    def readJSON(self, filepath: str) -> None:
        
        # Open file and read JSON
        with open(filepath, 'r') as f:
            json_dict = load(f)

        # Check for identifier
        if ("type" not in json_dict):
            raise KeyError(f"Invalid EnvironmentConfig JSON file (no \"type\" field found).")
        identifier = json_dict["type"]
        if (identifier != "EnvironmentConfig"):
            raise ValueError(f"Invalid EnvironmentConfig JSON file (\"type\" field is {identifier}).")
        
        # Assign fields to JSON data
        self.addressRB = json_dict["addressRB"]

        # Convert object dicts to objects
        self.PSUConfigList.clear()
        for config in json_dict["PSUConfigList"]:
            self.PSUConfigList.append(PSUConfig(vars_dict=config))
