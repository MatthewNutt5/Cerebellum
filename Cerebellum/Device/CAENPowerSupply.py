"""
This file contains the CAENPowerSupply class, which is an implementation of the
PowerSupply interface for a CAEN HV power supply. In this implementation,
a CAENPowerSupply specifically represents a single board in a CAEN crate.

Adapted in part from Tao Huang's implementation code.

An individual CAEN system, a "crate", has a number of "slots" for individual
PSUs. Each "slot" houses a "board", which has its own "channels" that power
can be delivered from.
"""

from Cerebellum.Device.PowerSupply import PowerSupply, PowerSupplyConfig

from caen_libs import caenhvwrapper
from typing import Any
import logging



class CAENPowerSupplyConfig(PowerSupplyConfig):

    # *_title = String to show as field title in GUI (e.g. COM Port: _____)
    # Any field without a corresponding field_title will default to the field name
    system_type_title   = "System Type"
    link_type_title     = "Link Type"
    ip_title            = "IP Address"
    username_title      = "Username"
    password_title      = "Password"
    board_slot_title    = "Board Slot #"

    # *_options = Options for field to provide in a dropdown menu
    # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type
    system_type_options = [
        "SY1527", "SY2527", "SY4527", "SY5527", "N568", "V65XX", "N1470",
        "V8100", "N568E", "DT55XX", "FTK", "DT55XXE", "N1068", "SMARTHV",
        "NGPS", "N1168", "R6060"
    ]
    link_type_options = [
        "TCPIP"
        # Possible, but not supported: "RS232", "CAENET", "USB", "OPTLINK", "USB_VCP", "USB3", "A4818"
    ]

    # Either init with default values or init with input fields (read from JSON)
    def __init__(self, vars_dict: dict[str, Any] = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            self.display_name   : str   = "CAEN Power Supply"       # Display name of the power supply
            self.system_type    : str   = "SY4527"                  # CAEN crate system type
            self.link_type      : str   = "TCPIP"                   # CAEN crate link type
            self.ip             : str   = ""                        # CAEN crate IP address
            self.username       : str   = ""                        # Username for logging into CAEN crate
            self.password       : str   = ""                        # Password for logging into CAEN crate
            self.board_slot     : int   = 0                         # Board slot of PSU to initialize



class CAENPowerSupply(PowerSupply):

    """
    Interface Methods ======================================================
    """

    # Initialize connection, possibly log ID
    def __init__(self, config: CAENPowerSupplyConfig):

        self.config = config
        
        all_system_type = [i.name for i in caenhvwrapper.SystemType]
        all_link_type = [i.name for i in caenhvwrapper.LinkType]
        if self.config.system_type not in all_system_type:
            raise KeyError(f"Invalid system_type from CAEN HV config ({self.config.system_type}). Available choices: {all_system_type}")
        if self.config.link_type not in all_link_type:
            raise KeyError(f"Invalid link_type from CAEN HV config ({self.config.link_type}). Available choices: {all_link_type}")
        
        try:
            self.device = caenhvwrapper.Device.open(
                caenhvwrapper.SystemType[self.config.system_type],
                caenhvwrapper.LinkType[self.config.link_type],
                self.config.ip,
                self.config.username,
                self.config.password)
            all_slots = self.device.get_crate_map() # Also does some initialization
            self.board = all_slots[self.config.board_slot]
            if (self.board is None):
                raise IndexError(f"Invalid board_slot from CAEN HV config ({self.config.board_slot}). Available choices: {[board.slot for board in all_slots if board is not None]}")
            logging.info(f"Opened CAENPowerSupply at socket ({self.config.ip}).")
            logging.info(self.get_id())
        except Exception as e:
            raise RuntimeError(f"Failed to open CAENPowerSupply at socket ({self.config.ip}): {e}")

    # Attempt to close any open connections when deallocated
    def __del__(self):
        if ("device" in vars(self)) and self.device:
            self.device.close()
            logging.info(f"Closed CAENPowerSupply at socket ({self.config.ip}).")
    
    # Get any identification data
    def get_id(self) -> str:
        slot = self.board.slot
        model = self.board.model
        description = self.board.description
        return f"Slot: {slot}, Model: {model}, Description: {description}"

    # Set the voltage setting of the given channel
    def set_voltage(self, channel: int, voltage: float) -> None:
        self._set_channel_parameter(channel, 'V0SET', voltage)

    # Set the current setting of the given channel
    def set_current(self, channel: int, current: float) -> None:
        self._set_channel_parameter(channel, 'I0SET', current)

    # Get the voltage setting of the given channel
    def get_voltage(self, channel: int) -> float:
        return float(self._get_channel_parameter(channel, 'V0SET'))

    # Get the current setting of the given channel
    def get_current(self, channel: int) -> float:
        return float(self._get_channel_parameter(channel, 'I0SET'))
    
    # Measure the voltage at the given channel
    def measure_voltage(self, channel: int) -> float:
        return float(self._get_channel_parameter(channel, 'VMON'))
    
    # Measure the current at the given channel
    def measure_current(self, channel: int) -> float:
        return float(self._get_channel_parameter(channel, 'IMON'))

    # Measure the power at the given channel
    def measure_power(self, channel: int) -> float:
        return self.measure_voltage(channel) * self.measure_current(channel)
    
    # Disable the given channel
    def disable_channel(self, channel: int) -> None:
        self._set_channel_parameter(channel, 'Pw', 0)
    
    # Enable the given channel
    def enable_channel(self, channel: int) -> None:
        self._set_channel_parameter(channel, 'Pw', 1)

    # Return the enable/disable state of the given channel
    def get_channel_state(self, channel: int) -> bool:
        return bool(self._get_channel_parameter(channel, 'Pw'))
    
    # Shutdown all channels
    def shutdown(self) -> None:
        for channel in range(self.board.n_channel):
            self.disable_channel(channel)



    """
    Helper Methods =========================================================
    """

    # NOTE: May need to convert exponent/decimal? See https://github.com/caenspa/py-caen-libs/blob/main/src/caen_libs/_caenhvwrappertypes.py#L257
    def _get_channel_parameter(self, channel: int, parameter: str) -> str | float | int:
        
        if parameter not in self.device.get_ch_param_info(self.board.slot, channel):
            raise KeyError(f"Invalid CAEN HV channel parameter ({parameter}). Available choices: {self.device.get_sys_prop_list()}")
        param_prop = self.device.get_ch_param_prop(self.board.slot, channel, parameter)
        if param_prop.mode is not caenhvwrapper.ParamMode.WRONLY:
            # Return type could be str, float, or int; convert as necessary
            return self.device.get_ch_param(self.board.slot, [channel], parameter)[0]
        else:
            raise KeyError(f"CAEN HV channel parameter ({parameter}) is write-only.")

    def _set_channel_parameter(self, channel: int, parameter: str, value: str | float | int) -> None:

        if parameter not in self.device.get_ch_param_info(self.board.slot, channel):
            raise KeyError(f"Invalid CAEN HV channel parameter ({parameter}). Available choices: {self.device.get_sys_prop_list()}")
        param_prop = self.device.get_ch_param_prop(self.board.slot, channel, parameter)
        if param_prop.mode is not caenhvwrapper.ParamMode.RDONLY:
            self.device.set_ch_param(self.board.slot, [channel], parameter, value)
        else:
            raise KeyError(f"CAEN HV channel parameter ({parameter}) is read-only.")
