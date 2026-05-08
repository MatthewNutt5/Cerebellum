"""
Device.py
This file contains the Device and DeviceConfig abstract classes, which act as
a parent class for all devices to extend from. A DeviceConfig contains all of
the necessary information for initializing a Device; a Device represents a
physical tool (e.g. power supply) that commands can be sent to. Generally, any
Device implementation should hide any complex libraries/communication protocols
behind simple function names. Device functions are then used by Events to carry
out certain commands.
"""

# Prevents TypeError on type hints for Python 3.7 to 3.9
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any



"""
DeviceConfig
This class, and all of its children, contain the necessary information for
initializing their corresponding Device class. For example, an SCPIPowerSupplyConfig
contains protocol information for constructing an SCPIPowerSupply, aka connecting
to a physical power supply that accepts SCPI commands. 
"""
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



"""
Device
This class, and all of its children, represent a physical device that commands
can be sent to. Every Device should handle an initialization routine (using the
corresponding DeviceConfig), a delete routine (for disconnecting from the device),
an ID-retrieval function, and a shutdown function - though it may suffice to
do nothing in these functions, depending on how the device behaves.
"""
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

    # Shutdown (i.e. disable, not disconnect) the device
    @abstractmethod
    def shutdown(self) -> None:
        pass
