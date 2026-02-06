"""
EnvironmentConfig.py
This file contains the EnvironmentConfig class, which is used to specify
the control structure of a given test stand - IP addresses, interface types,
etc. Ideally, the environment configuration is determined once and will not
change between test cycles. Configurations can be stored in JSON files for
later use.

Definitions
    - Outgoing Dependency: "This power supply must see a voltage of at least _
    coming from PSU X before it will activate." For example, the HVPS will
    always check if the LVPS is operating before it will activate.
    - Incoming Dependency: "This power supply cannot deactivate until X is
    deactivated." Likewise, the LVPS must see that the HVPS is disabled before
    it will turn off.

This file also contains the PSUConfig class, which is a helper class used to
specify the control configuration of a power supply in the test environment.
TODO: support for interlock, DAQs, (cold box?)
TODO: add more interfaces (how do we handle CAN?)
"""

from json import dump, load

class EnvironmentConfig:

    def __init__(self):
        self.RBConfig = {
            "IP"            : "",           # Ethernet IP address of KCU
            "FiberPort"     : 0             # KCU fiber port for RB fiber-optic
            }
        self.LVPSConfig     = PSUConfig()   # PSUConfig for LVPS
        self.HVPSConfig     = PSUConfig()   # PSUConfig for HVPS
        self.LVPSDependency = 0.0           # Minimum required voltage of LVPS for HVPS to activate
        self.auxPSUConfig   = []            # List of PSUConfig objects

    def newAuxPSU(self):
        self.auxPSUConfig.append(PSUConfig())
    
    def removeAuxPSU(self, index):
        self.auxPSUConfig.pop(index) 



    """
    Writes the contents of the object to the given filepath in the JSON format. 
    """
    def writeJSON(self, filepath):

        # Convert all objects to dicts
        vars_dict = self.__dict__.copy()
        vars_dict["LVPSConfig"] = vars(self.LVPSConfig)
        vars_dict["HVPSConfig"] = vars(self.HVPSConfig)
        for PSU in vars_dict["AuxPSUConfig"]:
            PSU = vars(PSU)
        
        # Open file and write JSON
        with open(filepath, 'w') as f:
            dump(vars_dict, f, indent=4)



    """
    Reads the given filepath for a JSON representation of a configuration;
    populates the fields of the object with the values.
    """
    def readJSON(self, filepath):
        
        # Open file and read JSON
        with open(filepath, 'r') as f:
            self.__dict__ = load(f)

        # Convert object dicts to objects
        self.LVPSConfig = PSUConfig(vars_dict=self.LVPSConfig)
        self.HVPSConfig = PSUConfig(vars_dict=self.HVPSConfig)
        for PSU in self.AuxPSUConfig:
            PSU = PSUConfig(vars_dict=PSU)



class PSUConfig:

    def __init__(self, vars_dict={}):
        if vars_dict:
            self.__dict__ = vars_dict.copy()
        else:
            self.connector      = ""    # Physical connector (Ethernet or USB)
            self.IP             = ""    # Ethernet IP address
            self.COM            = 0     # USB COM port
            self.interface      = ""    # Software interface (SCPI, BK)
            self.channel        = 0     # PSU channel number
            self.currentLimit   = 0.0   # Current limit, in amps
