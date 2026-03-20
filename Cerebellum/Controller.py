"""
EnvironmentControl.py
This file contains the EnvironmentControl library, which is used to send
commands and receive data from the devices of the test environment. The primary
function is run_test, which executes the test specified by a TestConfig object
on the test environment specified by an EnvironmentConfig object.

This file also contains several helper classes and functions.
"""

# Always make sure that Cerebellum and its submodules are on the import path
import sys, os
ABS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ABS_DIR)                # Cerebellum modules
sys.path.append(f"{ABS_DIR}/../")       # Cerebellum parent directory
sys.path.append(f"{ABS_DIR}/Device/")   # Device submodule
from Cerebellum.EnvironmentConfig import EnvironmentConfig
from Cerebellum.TestConfig import TestConfig
from Cerebellum.Event import *
from Cerebellum.Device.Device import Device, DeviceConfig, create_device
from Cerebellum.Device.PowerSupply import PowerSupply, PowerSupplyConfig

import logging, signal
logging.basicConfig(level=logging.INFO)



"""
Main Function + Helpers ========================================================
"""

def run_test(config: EnvironmentConfig, settings: TestConfig) -> None:
    
    # Attempt to run the regular program sequence
    try:
        
        # Before anything, check that each DeviceEvent will refer to the correct device
        logging.info("Verifying event list ==========")
        for event in settings.event_list:
            if isinstance(event, DeviceEvent):
                event.verify(config.device_config_list[event.device_idx])
        logging.info("All events verified successfully.")

        # Initialize all devices
        logging.info("Intializing devices ==========")
        device_list = _init_device_list(config.device_config_list)

        # Report and wait for user input
        logging.info("")
        logging.info("All devices initialized successfully.")
        logging.info("Verify the credentials appear as expected before continuing to event execution.")
        input("Press Enter to continue...")
        logging.info("")

        # Execute all events
        logging.info("Executing events ==========")
        _execEvents(settings.event_list, device_list)

        # Report and wait for user input
        logging.info("")
        logging.info("All events exeucted successfully.")
    
    # If there are any errors in normal operation, skip to disabling the PSUs
    # Block all external interrupts while doing so, and keep disabling the other
    # PSUs even if one of them fails
    # A standard Exception will end run_test prematurely
    # A BaseException (e.g. KeyboardInterrupt) will end the entire program
    except Exception as e:
        
        logging.error(f"During the testing routine, an exception was encountered: {e}")
        logging.error(f"Aborting testing routine.")
        pass

    finally:
        with _DelayedInterrupt([signal.SIGINT, signal.SIGTERM]):

            print()
            logging.info("")

            # If device_list has been initialized (i.e. all PSUs were initialized), shutdown all of them
            if "device_list" not in locals():
                logging.info("device_list has not been initialized. Skipping PSU shutdown.")
            else:
                logging.info("Disabling PSUs ==========")
                _shutdown(settings.shutdown_order, device_list)
                logging.info("")



def _init_device_list(device_config_list: list[DeviceConfig]) -> list[Device]:
    device_list = []
    for idx, device_config in enumerate(device_config_list):
        logging.info(f"Initializing device #{idx} ({device_config.display_name}) -----")
        device_list.append(create_device(device_config))
        
    return device_list



def _execEvents(event_list: list[Event], device_list: list[Device]) -> None:
    for idx, event in enumerate(event_list):

        logging.info(f"Executing event #{idx} -----")
        logging.info(f"{event.__class__.__name__}: {event.comment}")

        if isinstance(event, DeviceEvent):
            event.exec(device_list[event.device_idx])
        else:
            event.exec()



def _shutdown(shutdown_order: list[int], PSUList: list[PowerSupply]):

    if not shutdown_order:
        logging.info(f"Empty shutdown_order, defaulting to ascending order.")
        orderedPSUList = PSUList
        indexList = [i for i, _ in enumerate(PSUList)]

    elif ( set(shutdown_order) != set(range(len(PSUList))) ): # If the shutdown_order does not include each PSU index
        logging.warning(f"Invalid shutdown_order (does not include every PSU index), defaulting to ascending order.")
        orderedPSUList = PSUList
        indexList = [i for i, _ in enumerate(PSUList)]

    elif ( len(shutdown_order) != len(set(shutdown_order)) ): # If the shutdown_order has duplicate indices
        logging.warning(f"Invalid shutdown_order (duplicate indices), defaulting to ascending order.")
        orderedPSUList = PSUList
        indexList = [i for i, _ in enumerate(PSUList)]

    else:
        orderedPSUList = [PSUList[i] for i in shutdown_order]
        indexList = shutdown_order

    for idx, psu in zip(indexList, orderedPSUList):
        try:
            if psu:
                logging.info(f"Disabling PSU #{idx} -----")
                psu.shutdown()
        except Exception as e:
            logging.warning(f"While attemping to disable PSU #{idx}, an exception was encountered: {e}")
            pass



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
