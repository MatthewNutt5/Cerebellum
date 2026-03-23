"""
PowerSupply.py
This file contains the PowerSupply interface, which specifies the high-level
commands that EnvironmentControl will use.

This file also contains SCPIPowerSupply, which is an implementation of the
PowerSupply interface for an SCPI-controlled power supply, either over an IP
or a Serial connection.

Lastly, this file contains a factory function that will instantiate the correct
object based on the input PSUConfig. For example, a config with an SCPI
interface will be constructed as an SCPIPowerSupply.
"""

# Always make sure that Cerebellum and its submodules are on the import path
import sys, os
ABS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ABS_DIR)                # Device submodule
sys.path.append(f"{ABS_DIR}/../")       # Cerebellum modules
sys.path.append(f"{ABS_DIR}/../../")    # Cerebellum parent directory
from Cerebellum.Device.Device import Device, DeviceConfig

from abc import ABC, abstractmethod
import importlib



class PowerSupplyConfig(DeviceConfig):
    
    # *_title = String to show as field title in GUI (e.g. Display Name: _____)
    # Any field without a corresponding field_title will default to the field name

    # *_options = Options for field to provide in a dropdown menu
    # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type

    # Either init with default values or init with input fields (read from JSON)
    @abstractmethod
    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            self.display_name: str = "Power Supply"     # Display name of the power supply



class PowerSupply(Device):

    """
    Interface Methods ======================================================
    """
    
    # Initialize connection, possibly log ID
    @abstractmethod
    def __init__(self, config: PowerSupplyConfig):
        self.config = config

    # Attempt to close any open connections when deallocated
    @abstractmethod
    def __del__(self):
        pass
    
    # Get any identification data
    @abstractmethod
    def get_id(self) -> str:
        pass

    # Set the voltage setting of the given channel
    @abstractmethod
    def set_voltage(self, channel: int, voltage: float) -> None:
        pass

    # Set the current setting of the given channel
    @abstractmethod
    def set_current(self, channel: int, current: float) -> None:
        pass

    # Get the voltage setting of the given channel
    @abstractmethod
    def get_voltage(self, channel: int) -> float:
        pass

    # Get the current setting of the given channel
    @abstractmethod
    def get_current(self, channel: int) -> float:
        pass
    
    # Measure the voltage at the given channel
    @abstractmethod
    def measure_voltage(self, channel: int) -> float:
        pass
    
    # Measure the current at the given channel
    @abstractmethod
    def measure_current(self, channel: int) -> float:
        pass

    # Measure the power at the given channel
    @abstractmethod
    def measure_power(self, channel: int) -> float:
        pass
    
    # Disable the given channel
    @abstractmethod
    def disable_channel(self, channel: int) -> None:
        pass
    
    # Enable the given channel
    @abstractmethod
    def enable_channel(self, channel: int) -> None:
        pass

    # Return the enable/disable state of the given channel
    @abstractmethod
    def get_channel_state(self, channel: int) -> bool:
        pass
    
    # Shutdown all channels
    @abstractmethod
    def shutdown(self) -> None:
        pass
