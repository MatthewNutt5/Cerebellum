"""
This file contains the CAENPowerSupply class, which is an implementation of the
PowerSupply interface for a CAEN HV power supply.

Adapted from Tao Huang.
"""

from Cerebellum.EnvironmentConfig import PSUConfig
from Cerebellum.PowerSupply import PowerSupply

from pyparsing.helpers import wraps
from caen_libs import caenhvwrapper
from caen_libs._caenhvwrappertypes import Board
import logging

# PSUConfig.customConfig is a dict of string parameters you can pass through
# from Cerebellum. For this implementation,
# customConfig["systemType"]
# customConfig["linkType"]
# customConfig["username"]
# customConfig["password"]



class CAENPowerSupply(PowerSupply):

    config              : PSUConfig                 # Configuration of this power supply
    device              : caenhvwrapper.Device      # CAEN device object
    slots               : tuple[Board | None, ...]  # CAEN device slots
    systemProperties    : tuple[str, ...]           # CAEN device system properties

    """
    Interface Methods ======================================================
    """

    # Initialize connection, possibly log ID
    def __init__(self, config: PSUConfig):

        self.config = config
        systemType = self.config.customConfig["systemType"]
        linkType = self.config.customConfig["linkType"]
        username = self.config.customConfig["username"]
        password = self.config.customConfig["password"]
        
        allSystemType = [i.name for i in caenhvwrapper.SystemType]
        allLinkType = [i.name for i in caenhvwrapper.LinkType]
        if systemType not in allSystemType:
            raise KeyError(f"systemType from CAEN HV config ({systemType}) is invalid. Available choices: {allSystemType}")
        if linkType not in allLinkType:
            raise KeyError(f"linkType from CAEN HV config ({linkType}) is invalid. Available choices: {allLinkType}")
        
        try:
            self.device = caenhvwrapper.Device.open(
                caenhvwrapper.SystemType[systemType],
                caenhvwrapper.LinkType[linkType],
                self.config.IP,
                username,
                password)
            self.slots = self.device.get_crate_map()
            self.systemProperties = self.device.get_sys_prop_list()
            logging.info(f"Opened CAEN HV device at socket ({self.config.IP}): ", self.device)
        except caenhvwrapper.Error as e:
            raise RuntimeError(f"Failed to open CAEN HV device at socket ({self.config.IP}): {e}")

    # Attempt to close any open connections when deallocated
    @abstractmethod
    def __del__(self):
        pass
    
    # Get any identification data
    @abstractmethod
    def getID(self) -> str:
        pass

    # Set the voltage setting of the given channel
    @abstractmethod
    def setVoltage(self, voltage: float, channel: int) -> None:
        pass

    # Set the current setting of the given channel
    @abstractmethod
    def setCurrent(self, current: float, channel: int) -> None:
        pass

    # Get the voltage setting of the given channel
    @abstractmethod
    def getVoltage(self, channel: int) -> float:
        pass

    # Get the current setting of the given channel
    @abstractmethod
    def getCurrent(self, channel: int) -> float:
        pass
    
    # Measure the voltage at the given channel
    @abstractmethod
    def measureVoltage(self, channel: int) -> float:
        pass
    
    # Measure the current at the given channel
    @abstractmethod
    def measureCurrent(self, channel: int) -> float:
        pass

    # Measure the power at the given channel
    @abstractmethod
    def measurePower(self, channel: int) -> float:
        pass
    
    # Disable the given channel
    @abstractmethod
    def disableChannel(self, channel: int) -> None:
        pass
    
    # Enable the given channel
    @abstractmethod
    def enableChannel(self, channel: int) -> None:
        pass

    # Return the enable/disable state of the given channel
    @abstractmethod
    def getChannelState(self, channel: int) -> bool:
        pass
    
    # Shutdown all channels
    @abstractmethod
    def shutdown(self) -> None:
        pass
