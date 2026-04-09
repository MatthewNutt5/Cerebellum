"""
Placeholder
"""

import Cerebellum.Device, Cerebellum.Event
from Cerebellum.Device.Device import Device, DeviceConfig

from typing import Any
import logging, pkgutil, importlib, inspect



# Attempt to import all modules in Device
# Find all modules in Device that have a valid DeviceConfig constructor
# Create a dict of [device class name, device config constructor]
DEVICE_CONFIGS: dict[str, Any] = {}
for _, name, _ in pkgutil.walk_packages(Cerebellum.Device.__path__):
    full_name = "Cerebellum.Device." + name
    try:
        module = importlib.import_module(full_name)
    except Exception as e:
        logging.warning(f"Device submodule {full_name} failed to import: {e}")
        continue
    
    try:
        constructor = getattr(module, name + "Config")
        _ = constructor()
        DEVICE_CONFIGS[name] = constructor
    except Exception as e:
        if ("Can't instantiate abstract class" in str(e)): 
            logging.info(f"Skipping abstract config constructor {module.__name__}.{name + "Config"}()...")
        else:
            logging.warning(f"Failed to verify config constructor {module.__name__}.{name + "Config"}(): {e}")

# Find all modules in Device and get their Device constructors
# Create a dict of [device class name, device constructor]
# Since there is no "empty" configuration to validate with, this may include invalid constructors (e.g. PowerSupply())
DEVICES: dict[str, Any] = {}
for member_name, member in inspect.getmembers(Cerebellum.Device):
    if inspect.ismodule(member):
        try:
            constructor = getattr(member, member_name)
            DEVICES[member_name] = constructor
        except Exception as e:
            logging.warning(f"Failed to retrieve device constructor {member.__name__}.{member_name}(): {e}")

# Function to create a Device from its DeviceConfig
def create_device(config: DeviceConfig) -> Device:        
    
    # Get the instance constructor from DEVICES
    device_class_name = config.__class__.__name__.replace("Config", "")
    if (device_class_name in DEVICES):

        # Attempt to construct the Device using the config
        try:
            constructor = DEVICES[device_class_name]
            return constructor(config)
        except Exception as e:
            raise RuntimeError(f"Device constructor {device_class_name}() failed: {e}")
    
    else:
        raise ValueError(f"Device constructor {device_class_name}() not in DEVICES constructor list. Check if the {device_class_name} module is installed.")



# Find all events in Event that have a valid constructor
# Create a dict of [event class name, event constructor]
EVENTS: dict[str, Any] = {}
for member_name, member in inspect.getmembers(Cerebellum.Event):
    if inspect.isclass(member) and issubclass(member, Cerebellum.Event.Event):
        try:
            _ = member()
            EVENTS[member_name] = member
        except Exception as e:
            if ("Can't instantiate abstract class" in str(e)): 
                logging.info(f"Skipping abstract event constructor {member_name}()...")
            else:
                logging.warning(f"Failed to verify event constructor {member_name}(): {e}")
