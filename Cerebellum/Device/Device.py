"""
Placeholder
"""

from abc import ABC, abstractmethod
import importlib



class DeviceConfig(ABC):

    # *_title = String to show as field title in GUI (e.g. COM Port: _____)
    # Any field without a corresponding field_title will default to the field name
    display_name_title: str = "Display Name"
    
    # *_options = Options for field to provide in a dropdown menu
    # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type

    # Either init with default values or init with input fields (read from JSON)
    @abstractmethod
    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            self.display_name: str = "Device"   # Display name of the device



class Device(ABC):

    """
    Interface Methods ======================================================
    """

    # Initialize connection, possibly log ID
    @abstractmethod
    def __init__(self, config: DeviceConfig):
        self.config = config

    # Attempt to close any open connections when deallocated
    @abstractmethod
    def __del__(self):
        pass
    
    # Get any identification data
    @abstractmethod
    def get_id(self) -> str:
        pass



def create_device(config: DeviceConfig) -> Device:

    # From the config class_name, produce the module/instance name
    # E.g. config_class_name = "SCPIPowerSupplyConfig" --> module_name = "SCPIPowerSupply"
    config_class_name = config.__class__.__name__
    module_name = config_class_name.replace("Config", "")
    if (module_name == config_class_name):
        raise TypeError(f"Config class_name ({config_class_name}) does not have \"Config\" in its name; cannot produce module name.")
    
    # Import the instance constructor from the module
    try:
        module = importlib.import_module(f"Cerebellum.Device.{module_name}")
        constructor = getattr(module, module_name)
        return constructor(config)
    except Exception as e:
        raise RuntimeError(f"Device constructor Cerebellum.Device.{module_name}.{module_name}() failed: {e}")
