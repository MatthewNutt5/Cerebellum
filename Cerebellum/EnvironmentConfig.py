"""
EnvironmentConfig.py
This file contains the EnvironmentConfig class, which is used to specify
the control structure of a given test stand - IP addresses, interface types,
etc. Ideally, the environment configuration is determined once and will not
change between test cycles. Configurations can be stored in JSON files for
later use. Primarily used by EnvironmentControl.

Definitions
    - Outgoing Dependency: "This power supply must see a voltage of at least _
    coming from PSU X before it will activate." For example, the HVPS will
    always check if the LVPS is operating before it will activate.
    - Incoming Dependency: "This power supply cannot deactivate until X is
    deactivated." Likewise, the LVPS must see that the HVPS is disabled before
    it will turn off.

This file also contains the PSUConfig class, which is a helper class used
to specify the control configuration of a power supply in the test environment.
"""

from json import dump, load



class PSUConfig:

    displayName         : str
    interface           : str
    protocol            : str
    IP                  : str
    COM                 : str
    baudrate            : int
    implementationPath  : str
    implementationName  : str

    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            self.displayName        = "Power Supply"    # Display name of the power supply
            self.interface          = ""                # Communication interface (SCPI / Custom)
            self.protocol           = ""                # Communication protocol (IP / Serial)
            self.IP                 = ""                # IP address
            self.COM                = ""                # COM port (e.g. /dev/ttyACM0, COM1)
            self.baudrate           = 115200            # COM baudrate
            self.implementationPath = ""                # Filepath to implementation for Custom interface
            self.implementationName = ""                # Name of implementation class (i.e. constructor to call)



class EnvironmentConfig:

    addressRB           : str
    PSUConfigList       : list[PSUConfig]

    def __init__(self):
        self.addressRB      = ""                # Ethernet IP address of KCU
        self.PSUConfigList  = []                # List of PSUConfig objects

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
