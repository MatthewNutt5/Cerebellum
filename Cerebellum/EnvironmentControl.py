"""
EnvironmentControl.py
This file contains the EnvironmentControl library, which is used to send
commands and receive data from the devices of the test environment. The primary
function is runTest, which executes the test specified by a TestSettings object
on the test environment specified by an EnvironmentConfig object.

This file also contains several helper classes and functions.
"""

from Cerebellum.EnvironmentConfig import EnvironmentConfig, PSUConfig
from Cerebellum.TestSettings import TestSettings, Event
from Cerebellum.TestSettings import SetPSUEvent, EvalPSUVoltageEvent, EvalPSUCurrentEvent, EvalPSUPowerEvent
from Cerebellum.PowerSupply import PowerSupply, createPowerSupply

import logging, signal
logging.basicConfig(level=logging.INFO)



"""
Main Function + Helpers ========================================================
"""

def runTest(config: EnvironmentConfig, settings: TestSettings) -> None:
    
    # Attempt to run the regular program sequence
    try:

        # Initialize all PSUs
        logging.info("Intializing PSUs ==========")
        PSUList = _initPSUList(config.PSUConfigList)

        # Report and wait for user input
        logging.info("")
        logging.info("All PSUs initialized successfully.")
        logging.info("Verify the credentials appear as expected before continuing. (Next step: Set and enable PSUs)")
        input("Press Enter to continue...")
        logging.info("")

        # Set all PSUs to their assigned settings
        logging.info("Setting and enabling PSUs ==========")
        _setPSUList(settings.PSUSettingsList, PSUList)
        
        # Report and wait for user input
        logging.info("")
        logging.info("All PSUs set successfully.")
        logging.info("Verify the settings appear as expected before continuing. (Next step: Execute events)")
        input("Press Enter to continue...")
        logging.info("")

        # Execute all events
        logging.info("Executing events ==========")
        _execEvents(settings.eventList, PSUList)

        # Report and wait for user input
        logging.info("")
        logging.info("All criteria checked successfully. (Next step: Disable PSUs)")
        input("Press Enter to continue...")
    
    # If there are any errors in normal operation, skip to disabling the PSUs
    # Block all external interrupts while doing so, and keep disabling the other
    # PSUs even if one of them fails
    except Exception as e:
        logging.error(f"During the test sequence, an exception was encountered: {e}")
        logging.error(f"Aborting test sequence.")
        pass
    finally:
        with _DelayedInterrupt([signal.SIGINT, signal.SIGTERM]):
            # Turn off all PSUs
            print()
            logging.info("")
            logging.info("Disabling PSUs ==========")
            for idx, psu in enumerate(PSUList):
                try:
                    if psu:
                        logging.info(f"Disabling PSU #{idx} -----")
                        psu.shutdown()
                except Exception as e:
                    logging.warning(f"While attemping to disable PSU #{idx}, an exception was encountered: {e}")
                    pass
            logging.info("")

def _initPSUList(PSUConfigList: list[PSUConfig]) -> list[PowerSupply]:
    PSUList = []
    for idx, psu in enumerate(PSUConfigList):
        logging.info(f"Initializing PSU #{idx} ({psu.displayName})")
        PSUList.append(createPowerSupply(psu))
    return PSUList

def _setPSUList(PSUSettingsList: list[SetPSUEvent], PSUList: list[PowerSupply]) -> None:
    for idx, event in enumerate(PSUSettingsList):
        logging.info(f"Executing PSU setting #{idx} -----")
        _setPSU(event, PSUList[event.PSUidx])

def _execEvents(eventList: list[Event], PSUList: list[PowerSupply]) -> None:
    for idx, event in enumerate(eventList):
        logging.info(f"Executing event #{idx} -----")
        if isinstance(event, SetPSUEvent):
            _setPSU(event, PSUList[event.PSUidx])
        elif isinstance(event, EvalPSUVoltageEvent):
            if (_evalPSUVoltage(event, PSUList[event.PSUidx])):
                logging.info("PASS")
            else:
                logging.info("FAIL")
        elif isinstance(event, EvalPSUCurrentEvent):
            if (_evalPSUCurrent(event, PSUList[event.PSUidx])):
                logging.info("PASS")
            else:
                logging.info("FAIL")
        elif isinstance(event, EvalPSUPowerEvent):
            if (_evalPSUPower(event, PSUList[event.PSUidx])):
                logging.info("PASS")
            else:
                logging.info("FAIL")
        else:
            raise ValueError(f"Invalid Event type: {type(event)}")



"""
Event Handlers =================================================================
"""

def _setPSU(event: SetPSUEvent, psu: PowerSupply) -> None:
    logging.info("SetPSUEvent:")
    logging.info(f"Setting channel {event.channel} of PSU #{event.PSUidx} to {event.voltage} V and {event.current} A.")

    # Set voltage and verify that the setting succeeded
    psu.setVoltage(event.channel, event.voltage)
    actualSetVoltage = psu.getVoltage(event.channel)
    if (actualSetVoltage != event.voltage):
        raise RuntimeError(f"Voltage setting of channel {event.channel} of PSU #{event.PSUidx} ({actualSetVoltage} V) does not match expected setting ({event.voltage} V). The desired setting may be out-of-range for this PSU.")
    
    # Set current and verify that the setting succeeded
    psu.setCurrent(event.channel, event.current)
    actualSetCurrent = psu.getCurrent(event.channel)
    if (actualSetCurrent != event.current):
        raise RuntimeError(f"Current setting of channel {event.channel} of PSU #{event.PSUidx} ({actualSetCurrent} A) does not match expected setting ({event.current} A). The desired setting may be out-of-range for this PSU.")
    
    # Enable/disable the power supply
    if event.enable:
        logging.info(f"Enabling channel {event.channel} of PSU #{event.PSUidx}.")
        psu.enableChannel(event.channel)
    else:
        logging.info(f"Disabling channel {event.channel} of PSU #{event.PSUidx}.")
        psu.disableChannel(event.channel)

def _evalPSUVoltage(event: EvalPSUVoltageEvent, psu: PowerSupply) -> bool:
    logging.info("EvalPSUVoltageEvent:")
    logging.info(f"Measured voltage of PSU #{event.PSUidx} must be >= {event.VoltageLow} V and <= {event.VoltageHigh} V.")

    # Measure the voltage and compare against the valid range
    measured = psu.measureVoltage(event.channel)
    logging.info(f"Measured voltage of PSU #{event.PSUidx}: {measured} V")
    if (measured >= event.VoltageLow) and (measured <= event.VoltageHigh):
        return True
    else:
        return False

def _evalPSUCurrent(event: EvalPSUCurrentEvent, psu: PowerSupply) -> bool:
    logging.info("EvalPSUCurrentEvent:")
    logging.info(f"Measured current of PSU #{event.PSUidx} must be >= {event.CurrentLow} A and <= {event.CurrentHigh} A.")

    # Measure the current and compare against the valid range
    measured = psu.measureCurrent(event.channel)
    logging.info(f"Measured current of PSU #{event.PSUidx}: {measured} A")
    if (measured >= event.CurrentLow) and (measured <= event.CurrentHigh):
        return True
    else:
        return False
    
def _evalPSUPower(event: EvalPSUPowerEvent, psu: PowerSupply) -> bool:
    logging.info("EvalPSUPowerEvent:")
    logging.info(f"Measured power of PSU #{event.PSUidx} must be >= {event.PowerLow} W and <= {event.PowerHigh} W.")

    # Measure the power and compare against the valid range
    measured = psu.measurePower(event.channel)
    logging.info(f"Measured power of PSU #{event.PSUidx}: {measured} W")
    if (measured >= event.PowerLow) and (measured <= event.PowerHigh):
        return True
    else:
        return False



"""
Interrupt Delayer ==============================================================
"""

# Adapted from https://gist.github.com/tcwalther/ae058c64d5d9078a9f333913718bba95
class _DelayedInterrupt(object):
    def __init__(self, signals):
        if not isinstance(signals, list) and not isinstance(signals, tuple):
            signals = [signals]
        self.sigs = signals

    def __enter__(self):
        self.signal_received = {}
        self.old_handlers = {}
        for sig in self.sigs:
            self.signal_received[sig] = False
            self.old_handlers[sig] = signal.getsignal(sig)
            def handler(s, frame, sig=sig):
                self.signal_received[sig] = (s, frame)
                logging.debug(f"Signal {s} received; delaying")
            self.old_handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, handler)

    def __exit__(self, type, value, traceback):
        for sig in self.sigs:
            signal.signal(sig, self.old_handlers[sig])
            if self.signal_received[sig] and self.old_handlers[sig]:
                self.old_handlers[sig](*self.signal_received[sig])
