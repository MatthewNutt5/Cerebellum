"""
Placeholder
"""

import Cerebellum.Device

from abc import ABC, abstractmethod
from typing import Any
import pkgutil, importlib, inspect



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



# Walk packages of Cerebellum.Device and get all the submodules into the cache
# Ignore any package that doesn't work
for _, name, _ in pkgutil.walk_packages(Cerebellum.Device.__path__):
    full_name = "Cerebellum.Device." + name
    try:
        importlib.import_module(full_name)
    except:
        pass

# Find all modules in Device and get their Device constructors
# Create a dict of [device class name, device constructor]
# This may include invalid constructors (e.g. PowerSupply())
DEVICES: dict[str, Any] = {}
for member_name, member in inspect.getmembers(Cerebellum.Device):
    if inspect.ismodule(member):
        try:
            constructor = getattr(member, member_name)
            DEVICES[member_name] = constructor
        except:
            pass



def create_device(config: DeviceConfig) -> Device:        
    
    # Import the instance constructor from the module
    try:
        device_class_name = config.__class__.__name__.replace("Config", "")
        constructor = DEVICES[device_class_name]
        return constructor(config)
    except Exception as e:
        raise RuntimeError(f"Device constructor {device_class_name}() failed: {e}")
