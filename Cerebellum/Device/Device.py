"""
Placeholder
"""

from abc import ABC, abstractmethod
import importlib



class DeviceConfig(ABC):

    # *_title = String to show as field title in GUI (e.g. Display Name: _____)
    # Any field without a corresponding field_title will default to the field name
    display_name_title: str = "Display Name"
    
    # *_options = Options for field to provide in a dropdown menu
    # Any field without a corresponding field_options will default to a text box

    # Either init with default values or init with input fields (read from JSON)
    @abstractmethod
    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            self.type           : str   = "DeviceConfig"  # The type of device config (i.e. class name), for JSON r/w
            self.display_name   : str   = "Device"        # Display name of the device



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
    # ___Config --> Use constructor ___ from module ___
    # e.g. SCPIPowerSupplyConfig --> SCPIPowerSupply
    config_name = config.__class__.__name__
    constructor_name = config_name.replace("Config", "")
    if (constructor_name == config_name):
        raise TypeError(f"Config object ({config_name}) does not have \"Config\" in its name; cannot produce constructor name.")
    try:
        module = importlib.import_module(f"Cerebellum.Device.{constructor_name}")
        constructor = getattr(module, constructor_name)
        return constructor(config)
    except Exception as e:
        raise TypeError(f"Generated Device module/constructor name (Cerebellum.Device.{constructor_name}.{constructor_name}) is invalid: {e}")
