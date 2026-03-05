"""
EnvironmentControl.py
This file contains the EnvironmentControl library, which is used to send
commands and receive data from the devices of the test environment. The primary
function is runTest, which executes the test specified by a TestSettings object
on the test environment specified by an EnvironmentConfig object.

This file also contains several helper classes and functions.
"""

from EnvironmentConfig import EnvironmentConfig, PSUConfig
from TestSettings import TestSettings, PSUSettings
from TestSettings import Event, EvalVoltageEvent, EvalCurrentEvent
from _PSU import _PSU

import logging, signal
logging.basicConfig(level=logging.INFO)



"""
Main Function + Helpers ========================================================
"""

def runTest(config: EnvironmentConfig, settings: TestSettings):
    
    # Attempt to run the regular program sequence
    try:

        # Initialize all PSUs
        logging.info("Intializing PSUs ==========")
        PSUList = _initPSUList(config.PSUConfigList, settings.PSUSettingsList)

        # Report and wait for user input
        logging.info("")
        logging.info("All PSUs initialized successfully.")
        logging.info("Verify the credentials appear as expected before continuing. (Next step: Setting PSUs to assigned levels)")
        input("Press Enter to continue...")
        logging.info("")

        # Set all PSUs to their assigned settings
        logging.info("Setting PSUs to assigned levels ==========")
        _setPSUList(PSUList, settings.PSUSettingsList)
        
        # Report and wait for user input
        logging.info("")
        logging.info("All PSUs set successfully.")
        logging.info("Verify the settings appear as expected before continuing. (Next step: Enabling PSUs)")
        input("Press Enter to continue...")
        logging.info("")

        # Turn on all PSUs
        logging.info("Enabling PSUs ==========")
        _enablePSUList(PSUList)

        # Report and wait for user input
        logging.info("")
        logging.info("All PSUs enabled successfully.")
        logging.info("Verify the PSUs are behaving as expected before continuing. (Next step: Evaluating test criteria)")
        input("Press Enter to continue...")
        logging.info("")

        # Execute all events
        logging.info("Executing events ==========")
        _execEvents(settings.eventList, PSUList)

        # Report and wait for user input
        logging.info("")
        logging.info("All criteria checked successfully. (Next step: Disabling PSUs)")
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
            logging.info("")
            logging.info("Disabling PSUs ==========")
            for idx, psu in enumerate(PSUList):
                try:
                    if psu:
                        logging.info(f"Disabling PSU #{idx} -----")
                        psu.turnOff()
                except Exception as e:
                    logging.warning(f"While attemping to disable PSU #{idx}, an exception was encountered: {e}")
                    pass
            logging.info("")

def _initPSUList(PSUConfigList: list[PSUConfig], PSUSettingsList: list[PSUSettings]):
    PSUList = []
    for idx, psu in enumerate(PSUConfigList):
        logging.info(f"Initializing PSU #{idx}")
        PSUList.append(_PSU(psu))
    return PSUList

def _setPSUList(PSUList: list[_PSU], PSUSettingsList: list[PSUSettings]):
    for idx, (psu, setting) in enumerate(zip(PSUList, PSUSettingsList)):
        if psu:
            logging.info(f"Setting PSU #{idx} -----")
            logging.info(f"Voltage: {setting.voltage}")
            logging.info(f"Current: {setting.current}")
            psu.turnOff()
            psu.setVoltage(setting.voltage)
            actualSetVoltage = psu.getVoltage()
            if (actualSetVoltage != setting.voltage):
                raise RuntimeError(f"Voltage setting of PSU #{idx} ({actualSetVoltage} V) does not match expected setting ({setting.voltage} V). The desired setting may be out-of-range for this PSU.")
            psu.setCurrent(setting.current)
            actualSetCurrent = psu.getCurrent()
            if (actualSetCurrent != setting.current):
                raise RuntimeError(f"Current setting of PSU #{idx} ({actualSetCurrent} A) does not match expected setting ({setting.current} A). The desired setting may be out-of-range for this PSU.")

def _enablePSUList(PSUList: list[_PSU]):
    for idx, psu in enumerate(PSUList):
        if psu:
            logging.info(f"Enabling PSU #{idx} -----")
            psu.turnOn()

def _execEvents(eventList: list[Event], PSUList: list[_PSU]):
    for idx, event in enumerate(eventList):
        logging.info(f"Executing event #{idx} -----")
        if isinstance(event, EvalVoltageEvent):
            if (_evalPSUVoltage(event, PSUList[event.PSUidx])):
                logging.info("PASS")
            else:
                logging.info("FAIL")
        elif isinstance(event, EvalCurrentEvent):
            if (_evalPSUCurrent(event, PSUList[event.PSUidx])):
                logging.info("PASS")
            else:
                logging.info("FAIL")
        else:
            raise ValueError(f"Invalid Event type: {type(event)}")



"""
Event Handlers =================================================================
"""

def _evalPSUVoltage(event: EvalVoltageEvent, psu: _PSU):
    logging.info(f"Measured voltage of PSU #{event.PSUidx} must be >= {event.VoltageLow} V and <= {event.VoltageHigh} V.")
    measured = psu.measureVoltage()
    logging.info(f"Measured voltage of PSU #{event.PSUidx}: {measured} V")
    if (measured >= event.VoltageLow) and (measured <= event.VoltageHigh):
        return True
    else:
        return False

def _evalPSUCurrent(event: EvalCurrentEvent, psu: _PSU):
    logging.info(f"Measured current of PSU #{event.PSUidx} must be >= {event.CurrentLow} A and <= {event.CurrentHigh} A.")
    measured = psu.measureCurrent()
    logging.info(f"Measured current of PSU #{event.PSUidx}: {measured} V")
    if (measured >= event.CurrentLow) and (measured <= event.CurrentHigh):
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
