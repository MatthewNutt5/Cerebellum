"""
Placeholder
"""

import Cerebellum.Device

from abc import ABC, abstractmethod
from typing import Any
import pkgutil, importlib



class DeviceConfig(ABC):

    # *_title = String to show as field title in GUI (e.g. COM Port: _____)
    # Any field without a corresponding field_title will default to the field name
    display_name_title: str = "Display Name"
    
    # *_options = Options for field to provide in a dropdown menu
    # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type

    # Either init with default values or init with input fields (read from JSON)
    @abstractmethod
    def __init__(self, vars_dict: dict[str, Any] = {}):
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



# Find all modules in Device and get their Device constructors
# Create a dict of [module_name, device constructor]
# This will include invalid constructors (e.g. PowerSupply())
# Do this AFTER defining Device and DeviceConfig so the other modules will work
DEVICES: dict[str, Any] = {}
for _, full_name, _ in pkgutil.walk_packages(Cerebellum.Device.__path__, Cerebellum.Device.__name__ + "."):
    try:
        module = importlib.import_module(full_name)
        module_name = full_name.split(".")[-1]
        constructor = getattr(module, module_name)
        DEVICES[module_name] = constructor
    except:
        pass



def create_device(config: DeviceConfig) -> Device:
    
    # Import the instance constructor from the module
    try:
        full_name = config.__module__
        module_name = full_name.split(".")[-1]
        constructor = DEVICES[module_name]
        return constructor(config)
    except Exception as e:
        raise RuntimeError(f"Device constructor {full_name}.{module_name}() failed: {e}")
