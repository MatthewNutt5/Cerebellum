"""
Placeholder
"""

# Always make sure that Cerebellum and its submodules are on the import path
import sys, os
sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Cerebellum.PowerSupply import PowerSupply

from abc import ABC, abstractmethod
import logging, time, subprocess
logging.basicConfig(level=logging.INFO)



"""
Event Interface ================================================================
"""
# A generic Event
class Event(ABC):

    type        : str       # The type of event (i.e. class name), for JSON r/w
    comment     : str       # User-defined comment

    # Either init with default values or init with input fields (read from JSON)
    @abstractmethod
    def __init__(self, vars_dict: dict = {}):
        pass

    # Execute the event
    @abstractmethod
    def exec(self):
        pass

# An Event that returns None
class NoneEvent(Event):

    # Execute the event; return None (e.g. setPSUEvent, sleepEvent, etc.)
    @abstractmethod
    def exec(self) -> None:
        pass

# An Event that returns None and uses a PSU
class NonePSUEvent(NoneEvent):

    PSUidx      : int       # Index of the PSU
    channel     : int       # PSU channel to impart these settings

    # Execute the event; return None (e.g. setPSUEvent, sleepEvent, etc.)
    @abstractmethod
    def exec(self, psu: PowerSupply) -> None:
        pass

# An Event that returns bool
class BoolEvent(Event):

    # Execute the event; return bool (e.g. Eval events)
    @abstractmethod
    def exec(self) -> bool:
        pass

# An Event that returns bool and uses a PSU
class BoolPSUEvent(BoolEvent):

    PSUidx      : int       # Index of the PSU
    channel     : int       # PSU channel to measure

    # Execute the event; return bool (e.g. Eval events)
    @abstractmethod
    def exec(self, psu: PowerSupply) -> bool:
        pass

"""
SleepEvent =====================================================================
"""
class SleepEvent(NoneEvent):

    seconds     : float     # Number of seconds to sleep for

    # Either init with default values or init with input fields (read from JSON)
    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            self.type           = "SleepEvent"
            self.comment        = ""
            self.seconds        = 3.0

    # Execute the event
    def exec(self) -> None:
        logging.info(f"Sleeping for {self.seconds}...")
        time.sleep(self.seconds)

"""
WaitEvent ======================================================================
"""
class WaitEvent(NoneEvent):

    # Either init with default values or init with input fields (read from JSON)
    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            self.type           = "WaitEvent"
            self.comment        = ""

    # Execute the event
    def exec(self) -> None:
        input("Press Enter to continue...")

"""
CommandEvent ===================================================================
"""
class CommandEvent(NoneEvent):

    command     : str     # Command to run as a subprocess

    # Either init with default values or init with input fields (read from JSON)
    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            self.type           = "CommandEvent"
            self.comment        = ""
            self.command        = ""

    # Execute the event
    def exec(self) -> None:
        logging.info(f"Executing command: {self.command}")
        try:
            subprocess.run(self.command)
        except Exception as e:
            logging.warning(f"During command execution, an exception was encountered: {e}")
            pass

"""
SetPSUEvent ====================================================================
"""
class SetPSUEvent(NonePSUEvent):

    enable      : bool      # Should the power supply be enabled or disabled?
    voltage     : float     # Voltage setting
    current     : float     # Current setting

    # Either init with default values or init with input fields (read from JSON)
    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            self.type           = "SetPSUEvent"
            self.comment        = ""
            self.PSUidx         = 0
            self.channel        = 0
            self.enable         = True
            self.voltage        = 0.0
            self.current        = 0.0

    # Execute the event
    def exec(self, psu: PowerSupply) -> None:
        logging.info(f"Setting channel {self.channel} of PSU #{self.PSUidx} to {self.voltage} V and {self.current} A.")

        # If disabling, disable BEFORE changing settings
        if not self.enable:
            logging.info(f"Disabling channel {self.channel} of PSU #{self.PSUidx} ({psu.config.displayName}).")
            psu.disableChannel(self.channel)

        # Set voltage and verify that the setting succeeded
        psu.setVoltage(self.channel, self.voltage)
        actualSetVoltage = psu.getVoltage(self.channel)
        if (actualSetVoltage != self.voltage):
            raise RuntimeError(f"Voltage setting of channel {self.channel} of PSU #{self.PSUidx} ({actualSetVoltage} V) does not match expected setting ({self.voltage} V). The desired setting may be out-of-range for this PSU.")
        
        # Set current and verify that the setting succeeded
        psu.setCurrent(self.channel, self.current)
        actualSetCurrent = psu.getCurrent(self.channel)
        if (actualSetCurrent != self.current):
            raise RuntimeError(f"Current setting of channel {self.channel} of PSU #{self.PSUidx} ({actualSetCurrent} A) does not match expected setting ({self.current} A). The desired setting may be out-of-range for this PSU.")
        
        # If enabling, enable AFTER changing settings
        if self.enable:
            logging.info(f"Enabling channel {self.channel} of PSU #{self.PSUidx} ({psu.config.displayName}).")
            psu.enableChannel(self.channel)

"""
EvalPSUVoltageEvent ============================================================
"""
class EvalPSUVoltageEvent(BoolPSUEvent):

    VoltageLow  : float # The measured voltage must be >= this voltage
    VoltageHigh : float # The measured voltage must be <= this voltage

    # Either init with default values or init with input fields (read from JSON)
    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            self.type           = "EvalPSUVoltageEvent"
            self.comment        = ""
            self.PSUidx         = 0
            self.channel        = 0
            self.VoltageLow     = 0.0
            self.VoltageHigh    = float('inf')
    
    # Execute the event
    def exec(self, psu: PowerSupply) -> bool:
        logging.info(f"Measured voltage of PSU #{self.PSUidx} must be >= {self.VoltageLow} V and <= {self.VoltageHigh} V.")

        # Measure the voltage and compare against the valid range
        measured = psu.measureVoltage(self.channel)
        logging.info(f"Measured voltage of PSU #{self.PSUidx}: {measured} V")
        if (measured >= self.VoltageLow) and (measured <= self.VoltageHigh):
            return True
        else:
            return False

"""
EvalPSUCurrentEvent ============================================================
"""
class EvalPSUCurrentEvent(BoolPSUEvent):

    CurrentLow  : float # The measured current must be >= this current
    CurrentHigh : float # The measured current must be <= this current

    # Either init with default values or init with input fields (read from JSON)
    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            self.type           = "EvalPSUCurrentEvent"
            self.comment        = ""
            self.PSUidx         = 0
            self.channel        = 0
            self.CurrentLow     = 0.0
            self.CurrentHigh    = float('inf')

    # Execute the event
    def exec(self, psu: PowerSupply) -> bool:
        logging.info(f"Measured current of PSU #{self.PSUidx} must be >= {self.CurrentLow} A and <= {self.CurrentHigh} A.")

        # Measure the current and compare against the valid range
        measured = psu.measureCurrent(self.channel)
        logging.info(f"Measured current of PSU #{self.PSUidx}: {measured} A")
        if (measured >= self.CurrentLow) and (measured <= self.CurrentHigh):
            return True
        else:
            return False

"""
EvalPSUPowerEvent ==============================================================
"""
class EvalPSUPowerEvent(BoolPSUEvent):

    PowerLow    : float # The measured power must be >= this power
    PowerHigh   : float # The measured power must be <= this power

    # Either init with default values or init with input fields (read from JSON)
    def __init__(self, vars_dict: dict = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            self.type           = "EvalPSUPowerEvent"
            self.comment        = ""
            self.PSUidx         = 0
            self.channel        = 0
            self.PowerLow       = 0.0
            self.PowerHigh      = float('inf')

    # Execute the event
    def exec(self, psu: PowerSupply) -> bool:
        logging.info(f"Measured power of PSU #{self.PSUidx} must be >= {self.PowerLow} W and <= {self.PowerHigh} W.")

        # Measure the power and compare against the valid range
        measured = psu.measurePower(self.channel)
        logging.info(f"Measured power of PSU #{self.PSUidx}: {measured} W")
        if (measured >= self.PowerLow) and (measured <= self.PowerHigh):
            return True
        else:
            return False
