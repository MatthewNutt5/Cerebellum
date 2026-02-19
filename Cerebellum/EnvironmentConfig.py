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
TODO: add PSU dependencies to PSUConfig
TODO: support for interlock, DAQs, (cold box?)
TODO: add more interfaces (how do we handle CAN?)
"""

from json import dump, load



class EnvironmentConfig:

    def __init__(self):
        self.addressRB      = ""                # Ethernet IP address of KCU
        self.PSUConfigList  = []                # List of PSUConfig objects

    """
    Writes the contents of the object to the given filepath in the JSON format. 
    """
    def writeJSON(self, filepath: str):

        # Convert all objects to dicts
        vars_dict = vars(self).copy()
        vars_dict["PSUConfigList"] = [vars(PSU) for PSU in self.PSUConfigList]
        
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
        for index, PSU in enumerate(self.PSUConfigList):
            self.PSUConfigList[index] = PSUConfig(vars_dict=PSU)



class PSUConfig:

    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            self.protocol       = ""                # Communication protocol (IP / Serial)
            self.IP             = ""                # IP address
            self.COM            = ""                # COM port (e.g. /dev/ttyACM0, COM1)
            self.baudrate       = 115200            # COM baudrate
            self.interface      = ""                # Software interface (SCPI / CAN)
            self.channel        = 0                 # PSU channel number
