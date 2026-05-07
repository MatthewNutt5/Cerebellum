"""
Event.py
This file contains all events for execution during tests. There are two main
types of events - those that extend DeviceEvent and require a Device to operate
on, and those that extend Event and do not require a device. All events must
implement an exec() function, which is used to execute the event. DeviceEvents
receive an initialized Device object in their exec function, and must also
implement a verify() function, which is used to check if the given DeviceConfig
matches the event type.
"""

# Prevents TypeError on type hints for Python 3.7 to 3.9
from __future__ import annotations

from Cerebellum.Device.Device import Device, DeviceConfig
from Cerebellum.Device.PowerSupply import PowerSupply, PowerSupplyConfig

from abc import ABC, abstractmethod
from typing import Any
import logging, time, subprocess

TAMALERO_AVAIL = True
try:
    from Cerebellum.Device.TamaleroReadoutBoard import TamaleroReadoutBoard, TamaleroReadoutBoardConfig
except Exception as e:
    logging.warning(f"TamaleroReadoutBoard failed to import, skipping RBEvents...")
    TAMALERO_AVAIL = False

"""
Event Interface ================================================================
"""

# --- Event: A generic Event that doesn't require any device
class Event(ABC):

    # *_title = String to show as field title in GUI (e.g. COM Port: _____)
    # Any field without a corresponding field_title will default to the field name
    comment_title: str = "Comment"
    
    # *_options = Options for field to provide in a dropdown menu
    # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type

    # Either init with default values or init with input fields (read from JSON)
    @abstractmethod
    def __init__(self, vars_dict: dict[str, Any] = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            self.comment: str = ""      # User-defined comment

    # Execute the event
    @abstractmethod
    def exec(self) -> None:
        pass



# --- DeviceEvent: An Event that requires a generic device
class DeviceEvent(Event):

    # *_title = String to show as field title in GUI (e.g. COM Port: _____)
    # Any field without a corresponding field_title will default to the field name
    device_idx_title: str = "Device Index"
    
    # *_options = Options for field to provide in a dropdown menu
    # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type

    # Either init with default values or init with input fields (read from JSON)
    @abstractmethod
    def __init__(self, vars_dict: dict[str, Any] = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            super().__init__()          # Inits comment
            self.device_idx: int = 0    # Index of the device

    # Execute the event
    @abstractmethod
    def exec(self, device: Device) -> None:
        pass

    # Check that the given config is actually the config you want (in case an Event refers to the wrong device in device_config_list)
    @abstractmethod
    def verify(self, config: DeviceConfig) -> None:
        pass



# --- DeferredInit: Initialize the device during this event, instead of the initialization phase
class DeferredInit(DeviceEvent):

    # *_title = String to show as field title in GUI (e.g. COM Port: _____)
    # Any field without a corresponding field_title will default to the field name
    
    # *_options = Options for field to provide in a dropdown menu
    # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type

    # Either init with default values or init with input fields (read from JSON)
    def __init__(self, vars_dict: dict[str, Any] = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            super().__init__() # Inits comment and device_idx

    # Execute the event
    def exec(self, device: Device) -> None:
        # This event doesn't actually exec the way other events do; Controller
        # will instead init this device during the event
        pass

    # Check that the given config is actually the config you want (in case an Event refers to the wrong device in device_config_list)
    def verify(self, config: DeviceConfig) -> None:
        pass



"""
Device-less Events =============================================================
"""

# --- Sleep: Sleep for a float number of seconds
class Sleep(Event):

    # *_title = String to show as field title in GUI (e.g. COM Port: _____)
    # Any field without a corresponding field_title will default to the field name
    seconds_title: str = "Delay (s)"
    
    # *_options = Options for field to provide in a dropdown menu
    # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type

    # Either init with default values or init with input fields (read from JSON)
    def __init__(self, vars_dict: dict[str, Any] = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            super().__init__()          # Inits comment
            self.seconds: float = 3.0   # Number of seconds to sleep for

    # Execute the event
    def exec(self) -> None:
        logging.info(f"Sleeping for {self.seconds} seconds...")
        time.sleep(self.seconds)



# --- Checkpoint: Wait for user input before continuing
class Checkpoint(Event):

    # Either init with default values or init with input fields (read from JSON)
    def __init__(self, vars_dict: dict[str, Any] = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            super().__init__() # Inits comment

    # Execute the event
    def exec(self) -> None:
        input("Press Enter to continue...")



# --- ConsoleCommand: Run an arbitrary command as a subprocess
class ConsoleCommand(Event):

    # *_title = String to show as field title in GUI (e.g. COM Port: _____)
    # Any field without a corresponding field_title will default to the field name
    command_title: str = "Command"
    
    # *_options = Options for field to provide in a dropdown menu
    # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type

    # Either init with default values or init with input fields (read from JSON)
    def __init__(self, vars_dict: dict[str, Any] = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            super().__init__()          # Inits comment
            self.command: str = ""      # Command to run as a subprocess

    # Execute the event
    def exec(self) -> None:
        logging.info(f"Executing command: {self.command}")
        try:
            subprocess.run(self.command)
        except Exception as e:
            logging.warning(f"During command execution, an exception was encountered: {e}")
            pass



"""
PowerSupply Events =============================================================
"""

# --- PowerSupplyEvent: An Event that requires a PowerSupply device
class PowerSupplyEvent(DeviceEvent):

    # *_title = String to show as field title in GUI (e.g. COM Port: _____)
    # Any field without a corresponding field_title will default to the field name
    channel_title: str = "PSU Channel"
    
    # *_options = Options for field to provide in a dropdown menu
    # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type

    # Either init with default values or init with input fields (read from JSON)
    @abstractmethod
    def __init__(self, vars_dict: dict[str, Any] = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            super().__init__()          # Inits comment and device_idx
            self.channel: int = 0       # PSU channel

    # Execute the event
    @abstractmethod
    def exec(self, psu: PowerSupply) -> None:
        pass

    # Check that the given config is actually a PowerSupplyConfig (in case an Event refers to the wrong device in device_config_list)
    def verify(self, config: DeviceConfig) -> None:
        if not isinstance(config, PowerSupplyConfig):
            raise TypeError(f"Cannot run a PowerSupply Event on a non-PowerSupply Device; this Event likely has a faulty device_idx.")

# --- SetPSU: Change the settings of a PowerSupply at a particular channel
class SetPSU(PowerSupplyEvent):

    # *_title = String to show as field title in GUI (e.g. COM Port: _____)
    # Any field without a corresponding field_title will default to the field name
    enable_title    : str = "Enable/Disable Output"
    keep_title      : str = "Keep Voltage/Current Settings"
    voltage_title   : str = "Voltage (V)"
    current_title   : str = "Current (A)"
    
    # *_options = Options for field to provide in a dropdown menu
    # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type

    # Either init with default values or init with input fields (read from JSON)
    def __init__(self, vars_dict: dict[str, Any] = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            super().__init__()                  # Inits comment, device_idx, and channel
            self.enable     : bool  = True      # Should the channel be enabled or disabled?
            self.keep       : bool  = False     # Should the voltage/current settings be left alone?
            self.voltage    : float = 0.0       # Voltage setting
            self.current    : float = 0.0       # Current setting

    # Execute the event
    def exec(self, psu: PowerSupply) -> None:

        logging.info(f"Changing settings of PSU #{self.device_idx} ({psu.config.display_name}), channel {self.channel}.")
        
        # If disabling, disable BEFORE changing settings
        if not self.enable:
            if psu.get_channel_state(self.channel):
                logging.info(f"Disabling the channel.")
                psu.disable_channel(self.channel)
            else:
                logging.info(f"The channel is already disabled, skipping disable command.")

        # Change settings only if !keep
        if not self.keep:

            # Set voltage and verify that the setting succeeded
            if (psu.get_voltage(self.channel) == self.voltage):
                logging.info(f"The existing voltage setting already matches the expected setting, skipping set command.")
            else:
                logging.info(f"Setting voltage to {self.voltage} V.")
                psu.set_voltage(self.channel, self.voltage)
                actual_set_voltage = psu.get_voltage(self.channel)
                if (actual_set_voltage != self.voltage):
                    raise RuntimeError(f"The new voltage setting ({actual_set_voltage} V) does not match the expected setting ({self.voltage} V). The desired setting may be out of range for this PSU.")
            
            # Set current and verify that the setting succeeded
            if (psu.get_current(self.channel) == self.current):
                logging.info(f"The existing current setting already matches the expected setting, skipping set command.")
            else:
                logging.info(f"Setting current to {self.current} A.")
                psu.set_current(self.channel, self.current)
                actual_set_current = psu.get_current(self.channel)
                if (actual_set_current != self.current):
                    raise RuntimeError(f"The new current setting ({actual_set_current} A) does not match the expected setting ({self.current} A). The desired setting may be out of range for this PSU.")
        
        # If enabling, enable AFTER changing settings
        if self.enable:
            if psu.get_channel_state(self.channel):
                logging.info(f"The channel is already enabled, skipping enable command.")
            else:
                logging.info(f"Enabling the channel.")
                psu.enable_channel(self.channel)



# --- EvalPSUVoltage: Evaluate a PowerSupply's measured voltage at a particular channel
class EvalPSUVoltage(PowerSupplyEvent):

    # *_title = String to show as field title in GUI (e.g. COM Port: _____)
    # Any field without a corresponding field_title will default to the field name
    voltage_low_title   : str = "Lower Bound (V)"
    voltage_high_title  : str = "Upper Bound (V)"
    
    # *_options = Options for field to provide in a dropdown menu
    # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type

    # Either init with default values or init with input fields (read from JSON)
    def __init__(self, vars_dict: dict[str, Any] = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            super().__init__()                              # Inits comment, device_idx, and channel
            self.voltage_low    : float = float('-inf')     # The measured voltage must be >= this voltage
            self.voltage_high   : float = float('inf')      # The measured voltage must be <= this voltage
    
    # Execute the event
    def exec(self, psu: PowerSupply) -> None:

        logging.info(f"Measured voltage from PSU #{self.device_idx} ({psu.config.display_name}), channel {self.channel}, must be >= {self.voltage_low} V and <= {self.voltage_high} V.")

        # Measure the voltage and compare against the valid range
        measured = psu.measure_voltage(self.channel)
        logging.info(f"Measured voltage: {measured} V")
        if (measured >= self.voltage_low) and (measured <= self.voltage_high):
            logging.info("PASS")
        else:
            logging.info("FAIL")



# --- EvalPSUCurrent: Evaluate a PowerSupply's measured current at a particular channel
class EvalPSUCurrent(PowerSupplyEvent):

    # *_title = String to show as field title in GUI (e.g. COM Port: _____)
    # Any field without a corresponding field_title will default to the field name
    current_low_title   : str = "Lower Bound (A)"
    current_high_title  : str = "Upper Bound (A)"
    
    # *_options = Options for field to provide in a dropdown menu
    # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type

    # Either init with default values or init with input fields (read from JSON)
    def __init__(self, vars_dict: dict[str, Any] = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            super().__init__()                              # Inits comment, device_idx, and channel
            self.current_low    : float = float('-inf')     # The measured current must be >= this current
            self.current_high   : float = float('inf')      # The measured current must be <= this current

    # Execute the event
    def exec(self, psu: PowerSupply) -> None:

        logging.info(f"Measured current from PSU #{self.device_idx} ({psu.config.display_name}), channel {self.channel}, must be >= {self.current_low} A and <= {self.current_high} A.")

        # Measure the current and compare against the valid range
        measured = psu.measure_current(self.channel)
        logging.info(f"Measured current: {measured} A")
        if (measured >= self.current_low) and (measured <= self.current_high):
            logging.info("PASS")
        else:
            logging.info("FAIL")



# --- EvalPSUPower: Evaluate a PowerSupply's measured power at a particular channel
class EvalPSUPower(PowerSupplyEvent):

    # *_title = String to show as field title in GUI (e.g. COM Port: _____)
    # Any field without a corresponding field_title will default to the field name
    power_low_title     : str = "Lower Bound (W)"
    power_high_title    : str = "Upper Bound (W)"
    
    # *_options = Options for field to provide in a dropdown menu
    # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type

    # Either init with default values or init with input fields (read from JSON)
    def __init__(self, vars_dict: dict[str, Any] = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            super().__init__()                              # Inits comment, device_idx, and channel
            self.power_low      : float = float('-inf')     # The measured power must be >= this power
            self.power_high     : float = float('inf')      # The measured power must be <= this power

    # Execute the event
    def exec(self, psu: PowerSupply) -> None:

        logging.info(f"Measured power from PSU #{self.device_idx} ({psu.config.display_name}), channel {self.channel}, must be >= {self.power_low} W and <= {self.power_high} W.")

        # Measure the power and compare against the valid range
        measured = psu.measure_power(self.channel)
        logging.info(f"Measured power: {measured} W")
        if (measured >= self.power_low) and (measured <= self.power_high):
            logging.info("PASS")
        else:
            logging.info("FAIL")



"""
TamaleroReadoutBoard Events ====================================================
"""

if TAMALERO_AVAIL:

    # --- RBEvent: An Event that requires a TamaleroReadoutBoard device
    class RBEvent(DeviceEvent):

        # *_title = String to show as field title in GUI (e.g. COM Port: _____)
        # Any field without a corresponding field_title will default to the field name
        
        # *_options = Options for field to provide in a dropdown menu
        # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type

        # Either init with default values or init with input fields (read from JSON)
        @abstractmethod
        def __init__(self, vars_dict: dict[str, Any] = {}):
            if vars_dict:
                vars(self).update(vars_dict) # Install input into __dict__
            else:
                super().__init__() # Inits comment and device_idx

        # Execute the event
        @abstractmethod
        def exec(self, rb: TamaleroReadoutBoard) -> None:
            pass

        # Check that the given config is actually a TamaleroReadoutBoardConfig (in case an Event refers to the wrong device in device_config_list)
        def verify(self, config: DeviceConfig) -> None:
            if not isinstance(config, TamaleroReadoutBoardConfig):
                raise TypeError(f"Cannot run a RBEvent on a non-RB Device; this Event likely has a faulty device_idx.")



    # --- RBReadADC: Read ADCs of all onboard chips
    class RBReadADC(RBEvent):
        
        # *_title = String to show as field title in GUI (e.g. COM Port: _____)
        # Any field without a corresponding field_title will default to the field name
        
        # *_options = Options for field to provide in a dropdown menu
        # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type

        # Either init with default values or init with input fields (read from JSON)
        def __init__(self, vars_dict: dict[str, Any] = {}):
            if vars_dict:
                vars(self).update(vars_dict) # Install input into __dict__
            else:
                super().__init__() # Inits comment and device_idx
        
        # Execute the event
        def exec(self, rb: TamaleroReadoutBoard) -> None:
            logging.info(f"RB ADC readings: {rb.read_adcs()}")



    # --- RBReadADC: Run built-in eyescan test on LPGBT ADCs
    class RBRunEyescan(RBEvent):

        # *_title = String to show as field title in GUI (e.g. COM Port: _____)
        # Any field without a corresponding field_title will default to the field name
        
        # *_options = Options for field to provide in a dropdown menu
        # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type

        # Either init with default values or init with input fields (read from JSON)
        def __init__(self, vars_dict: dict[str, Any] = {}):
            if vars_dict:
                vars(self).update(vars_dict) # Install input into __dict__
            else:
                super().__init__() # Inits comment and device_idx
        
        # Execute the event
        def exec(self, rb: TamaleroReadoutBoard) -> None:
            rb.run_eyescan()
            logging.info(f"RB LPGBT ADC eyescan test complete.")



    # --- RBReadPatternCheckers: Reset then read LPGBT pattern checkers
    class RBReadPatternCheckers(RBEvent):
        
        # *_title = String to show as field title in GUI (e.g. COM Port: _____)
        # Any field without a corresponding field_title will default to the field name
        
        # *_options = Options for field to provide in a dropdown menu
        # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type

        # Either init with default values or init with input fields (read from JSON)
        def __init__(self, vars_dict: dict[str, Any] = {}):
            if vars_dict:
                vars(self).update(vars_dict) # Install input into __dict__
            else:
                super().__init__() # Inits comment and device_idx
        
        # Execute the event
        def exec(self, rb: TamaleroReadoutBoard) -> None:
            logging.info(f"RB LPGBT pattern checker readings: {rb.read_pattern_checkers()}")



    # --- RBTestSCAI2C: Test I2C port of SCA chip
    class RBTestSCAI2C(RBEvent):

        # *_title = String to show as field title in GUI (e.g. COM Port: _____)
        # Any field without a corresponding field_title will default to the field name
        test_channel_title: str = "Test Channel"
        
        # *_options = Options for field to provide in a dropdown menu
        # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type

        # Either init with default values or init with input fields (read from JSON)
        def __init__(self, vars_dict: dict[str, Any] = {}):
            if vars_dict:
                vars(self).update(vars_dict) # Install input into __dict__
            else:
                super().__init__() # Inits comment and device_idx
                self.test_channel: int = 0
        
        # Execute the event
        def exec(self, rb: TamaleroReadoutBoard) -> None:
            logging.info(f"RB SCA I2C test results: {rb.test_sca_i2c(self.test_channel)}")
