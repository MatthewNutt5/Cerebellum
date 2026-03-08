"""
This file contains the CAENPowerSupply class, which is an implementation of the
PowerSupply interface for a CAEN HV power supply. In this implementation,
a CAENPowerSupply specifically represents a single board in a CAEN crate.

Adapted in part from Tao Huang's implementation code.

An individual CAEN system, a "crate", has a number of "slots" for individual
PSUs. Each "slot" houses a "board", which has its own "channels" that power
can be delivered from.
"""

from Cerebellum.EnvironmentConfig import PSUConfig
from Cerebellum.PowerSupply import PowerSupply

from caen_libs import caenhvwrapper
from caen_libs._caenhvwrappertypes import Board, ParamProp
import logging

# PSUConfig.customConfig is a dict of string parameters you can pass through
# from Cerebellum. For this implementation, the following parameters are used:
# customConfig["systemType"]
# customConfig["linkType"]
# customConfig["username"]
# customConfig["password"]
# customConfig["boardSlot"]



class CAENPowerSupply(PowerSupply):

    config              : PSUConfig                 # Configuration of this power supply
    device              : caenhvwrapper.Device      # CAEN device object
    board               : Board                     # Individual CAEN PSU board

    """
    Interface Methods ======================================================
    """

    # Initialize connection, possibly log ID
    def __init__(self, config: PSUConfig):

        self.config = config

        systemType = self.config.customConfig["systemType"]
        linkType = self.config.customConfig["linkType"]
        IP = self.config.IP
        username = self.config.customConfig["username"]
        password = self.config.customConfig["password"]
        boardSlot = int(self.config.customConfig["boardSlot"])
        
        allSystemType = [i.name for i in caenhvwrapper.SystemType]
        allLinkType = [i.name for i in caenhvwrapper.LinkType]
        if systemType not in allSystemType:
            raise KeyError(f"Invalid systemType from CAEN HV config ({systemType}). Available choices: {allSystemType}")
        if linkType not in allLinkType:
            raise KeyError(f"Invalid linkType from CAEN HV config ({linkType}). Available choices: {allLinkType}")
        
        try:
            self.device = caenhvwrapper.Device.open(
                caenhvwrapper.SystemType[systemType],
                caenhvwrapper.LinkType[linkType],
                IP,
                username,
                password)
            allSlots = self.device.get_crate_map() # Also does some initialization
            self.board = allSlots[boardSlot]
            if (self.board is None):
                raise IndexError(f"Invalid boardSlot from CAEN HV config ({boardSlot}). Available choices: {[board.slot for board in allSlots if board is not None]}")
            logging.info(f"Opened CAENPowerSupply at socket ({self.config.IP}).")
            logging.info(self.getID())
        except caenhvwrapper.Error as e:
            raise RuntimeError(f"Failed to open CAENPowerSupply at socket ({self.config.IP}): {e}")

    # Attempt to close any open connections when deallocated
    def __del__(self):
        if ("device" in vars(self)) and self.device:
            self.device.close()
            logging.info(f"Closed CAENPowerSupply at socket ({self.config.IP}).")
    
    # Get any identification data
    def getID(self) -> str:
        slot = self.board.slot
        model = self.board.model
        description = self.board.description
        return f"Slot: {slot}, Model: {model}, Description: {description}"

    # Set the voltage setting of the given channel
    def setVoltage(self, channel: int, voltage: float) -> None:
        self._setChannelParameter(channel, "V0SET", voltage)

    # Set the current setting of the given channel
    def setCurrent(self, channel: int, current: float) -> None:
        self._setChannelParameter(channel, "I0SET", current)

    # Get the voltage setting of the given channel
    # NOTE: May need to convert exponent/decimal?
    # NOTE: See https://github.com/caenspa/py-caen-libs/blob/main/src/caen_libs/_caenhvwrappertypes.py#L257
    def getVoltage(self, channel: int) -> float:
        return float(self._getChannelParameter(channel, "V0SET"))

    # Get the current setting of the given channel
    def getCurrent(self, channel: int) -> float:
        return float(self._getChannelParameter(channel, "I0SET"))
    
    # Measure the voltage at the given channel
    def measureVoltage(self, channel: int) -> float:
        return float(self._getChannelParameter(channel, "VMON"))
    
    # Measure the current at the given channel
    def measureCurrent(self, channel: int) -> float:
        return float(self._getChannelParameter(channel, "IMON"))

    # Measure the power at the given channel
    def measurePower(self, channel: int) -> float:
        return self.measureVoltage(channel) * self.measureCurrent(channel)
    
    # Disable the given channel
    def disableChannel(self, channel: int) -> None:
        self._setChannelParameter(channel, 'Pw', 0)
    
    # Enable the given channel
    def enableChannel(self, channel: int) -> None:
        self._setChannelParameter(channel, 'Pw', 1)

    # Return the enable/disable state of the given channel
    def getChannelState(self, channel: int) -> bool:
        return bool(self._getChannelParameter(channel, 'Pw'))
    
    # Shutdown all channels
    def shutdown(self) -> None:
        for channel in range(self.board.n_channel):
            self.disableChannel(channel)



    """
    Helper Methods =========================================================
    """

    def _getChannelParameter(self, channel: int, parameter: str) -> str | float | int:
        
        if parameter not in self.device.get_ch_param_info(self.board.slot, channel):
            raise KeyError(f"Invalid CAEN HV channel parameter ({parameter}). Available choices: {self.device.get_sys_prop_list()}")
        param_prop = self.device.get_ch_param_prop(self.board.slot, channel, parameter)
        if param_prop.mode is not caenhvwrapper.ParamMode.WRONLY:
            # Return type could be str, float, or int; convert as necessary
            return self.device.get_ch_param(self.board.slot, [channel], parameter)[0]
        else:
            raise KeyError(f"CAEN HV channel parameter ({parameter}) is write-only.")

    def _setChannelParameter(self, channel: int, parameter: str, value: str | float | int) -> None:

        if parameter not in self.device.get_ch_param_info(self.board.slot, channel):
            raise KeyError(f"Invalid CAEN HV channel parameter ({parameter}). Available choices: {self.device.get_sys_prop_list()}")
        param_prop = self.device.get_ch_param_prop(self.board.slot, channel, parameter)
        if param_prop.mode is not caenhvwrapper.ParamMode.RDONLY:
            self.device.set_ch_param(self.board.slot, [channel], parameter, value)
        else:
            raise KeyError(f"CAEN HV channel parameter ({parameter}) is read-only.")
