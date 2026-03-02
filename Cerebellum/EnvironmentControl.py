"""
EnvironmentControl.py
This file contains the EnvironmentControl library, which is used to send
commands and receive data from the devices of the test environment. The primary
function is runTest, which executes the test specified by a TestSettings object
on the test environment specified by an EnvironmentConfig object.

This file also contains several helper classes and functions.
"""

from EnvironmentConfig import EnvironmentConfig, PSUConfig
from TestSettings import TestSettings, PSUSettings, Criterion
from _PSU import _PSU

import logging, signal



"""
Main Test Function =============================================================
"""

def runTest(config: EnvironmentConfig, settings: TestSettings):
    
    # Attempt to run the regular program sequence
    try:

        # Initialize all PSUs
        print()
        print("Intializing PSUs ==========")
        PSUList = []
        for idx, psu in enumerate(config.PSUConfigList):
            if (settings.PSUSettingsList[idx].enable):
                print(f"Initializing PSU #{idx}")
                PSUList.append(_PSU(psu))
            else:
                print(f"PSU #{idx} is disabled, skipping initialization")
                PSUList.append(None)

        # Report and wait for user input
        print()
        print("All PSUs initialized successfully.")
        print("Verify the credentials appear as expected before continuing. (Next step: Setting PSUs to assigned levels)")
        input("Press Enter to continue...")
        print()

        # Set all PSUs to their assigned settings
        print("Setting PSUs to assigned levels ==========")
        for idx, (psu, setting) in enumerate(zip(PSUList, settings.PSUSettingsList)):
            if psu:
                print(f"Setting PSU #{idx} -----")
                print(f"Voltage: {setting.voltage}")
                print(f"Current: {setting.current}")
                psu.turnOff()
                psu.setVoltage(setting.voltage)
                actualSetVoltage = psu.getVoltage()
                if (actualSetVoltage != setting.voltage):
                    raise RuntimeError(f"Voltage setting of PSU #{idx} ({actualSetVoltage} V) does not match expected setting ({setting.voltage} V). The desired setting may be out-of-range for this PSU.")
                psu.setCurrent(setting.current)
                actualSetCurrent = psu.getCurrent()
                if (actualSetCurrent != setting.current):
                    raise RuntimeError(f"Current setting of PSU #{idx} ({actualSetCurrent} A) does not match expected setting ({setting.current} A). The desired setting may be out-of-range for this PSU.")
        
        # Report and wait for user input
        print()
        print("All PSUs set successfully.")
        print("Verify the settings appear as expected before continuing. (Next step: Enabling PSUs)")
        input("Press Enter to continue...")
        print()

        # Turn on all PSUs
        print("Enabling PSUs ==========")
        for idx, psu in enumerate(PSUList):
            if psu:
                print(f"Enabling PSU #{idx} -----")
                psu.turnOn()

        # Report and wait for user input
        print()
        print("All PSUs enabled successfully.")
        print("Verify the PSUs are behaving as expected before continuing. (Next step: Evaluating test criteria)")
        input("Press Enter to continue...")
        print()

        # Eval all criteria
        print("Evaluating test criteria ==========")
        for idx, criterion in enumerate(settings.criteriaList):
            if PSUList[criterion.PSUidx]:
                print(f"Evaluating criterion #{idx} -----")
                if (criterion.criterionType == "PSUCurrent"):
                    if (_evalPSUCurrent(criterion, PSUList[criterion.PSUidx])):
                        print("PASS")
                    else:
                        print("FAIL")
                elif (criterion.criterionType == "PSUVoltage"):
                    if (_evalPSUVoltage(criterion, PSUList[criterion.PSUidx])):
                        print("PASS")
                    else:
                        print("FAIL")
                else:
                    raise ValueError(f"Invalid criterionType value: {criterion.criterionType}")
            else:
                print(f"Criterion #{idx} refers to a disabled PSU (#{criterion.PSUidx}), skipping evaluation -----")

        # Report and wait for user input
        print()
        print("All criteria checked successfully. (Next step: Disabling PSUs)")
        input("Press Enter to continue...")
    
    # If there are any errors in normal operation, skip to disabling the PSUs
    # Block all external interrupts while doing so, and keep disabling the other
    # PSUs even if one of them fails
    finally:
        with _DelayedInterrupt([signal.SIGINT, signal.SIGTERM]):
            # Turn off all PSUs
            print()
            print("Disabling PSUs ==========")
            for idx, psu in enumerate(PSUList):
                try:
                    if psu:
                        print(f"Disabling PSU #{idx} -----")
                        psu.turnOff()
                except Exception as e:
                    logging.warning(f"While attemping to disable PSU #{idx}, an exception was encountered: {e}")
                    pass
            print()



"""
Criterion Evaluation ===========================================================
"""

def _evalPSUVoltage(criterion: Criterion, psu: _PSU):
    print(f"Measured voltage of PSU #{criterion.PSUidx} must be >= {criterion.PSUVoltageLow} V and <= {criterion.PSUVoltageHigh} V.")
    measured = psu.measureVoltage()
    print(f"Measured voltage of PSU #{criterion.PSUidx}: {measured} V")
    if (measured >= criterion.PSUVoltageLow) and (measured <= criterion.PSUVoltageHigh):
        return True
    else:
        return False

def _evalPSUCurrent(criterion: Criterion, psu: _PSU):
    print(f"Measured current of PSU #{criterion.PSUidx} must be >= {criterion.PSUCurrentLow} A and <= {criterion.PSUCurrentHigh} A.")
    measured = psu.measureCurrent()
    print(f"Measured current of PSU #{criterion.PSUidx}: {measured} V")
    if (measured >= criterion.PSUCurrentLow) and (measured <= criterion.PSUCurrentHigh):
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
                logging.info(f"Signal {s} received; delaying")
            self.old_handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, handler)

    def __exit__(self, type, value, traceback):
        for sig in self.sigs:
            signal.signal(sig, self.old_handlers[sig])
            if self.signal_received[sig] and self.old_handlers[sig]:
                self.old_handlers[sig](*self.signal_received[sig])
