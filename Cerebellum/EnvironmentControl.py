"""
EnvironmentControl.py
This file contains the EnvironmentControl library, which is used to send
commands and receive data from the devices of the test environment. The primary
function is runTest, which executes the test specified by a TestSettings object
on the test environment specified by an EnvironmentConfig object.

This file also contains several helper classes and functions.
"""

# Always make sure that Cerebellum and its submodules are on the import path
import sys, os
sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Cerebellum.EnvironmentConfig import EnvironmentConfig, PSUConfig
from Cerebellum.TestSettings import TestSettings
from Cerebellum.Event import *
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
        logging.info("Verify the credentials appear as expected before continuing to event execution.")
        input("Press Enter to continue...")
        logging.info("")

        # Execute all events
        logging.info("Executing events ==========")
        _execEvents(settings.eventList, PSUList)

        # Report and wait for user input
        logging.info("")
        logging.info("All events exeucted successfully.")
    
    # If there are any errors in normal operation, skip to disabling the PSUs
    # Block all external interrupts while doing so, and keep disabling the other
    # PSUs even if one of them fails
    # A standard Exception will end runTest prematurely
    # A BaseException (e.g. KeyboardInterrupt) will end the entire program
    except Exception as e:
        
        logging.error(f"During the testing routine, an exception was encountered: {e}")
        logging.error(f"Aborting testing routine.")
        pass

    finally:
        with _DelayedInterrupt([signal.SIGINT, signal.SIGTERM]):

            print()
            logging.info("")

            # If PSUList has been initialized (i.e. all PSUs were initialized), shutdown all of them
            if "PSUList" not in locals():
                logging.info("PSUList has not been initialized. Skipping shutdown.")
            else:
                logging.info("Disabling PSUs ==========")
                _shutdown(settings.shutdownOrder, PSUList)
                logging.info("")

def _initPSUList(PSUConfigList: list[PSUConfig]) -> list[PowerSupply]:
    PSUList = []
    for idx, psu in enumerate(PSUConfigList):
        logging.info(f"Initializing PSU #{idx} ({psu.displayName}) -----")
        PSUList.append(createPowerSupply(psu))

    return PSUList

def _execEvents(eventList: list[Event], PSUList: list[PowerSupply]) -> None:
    for idx, event in enumerate(eventList):

        logging.info(f"Executing event #{idx} -----")
        logging.info(f"{event.type}: {event.comment}")

        if isinstance(event, NoneEvent): # Events that return None...
            if isinstance(event, NonePSUEvent): # ...and use a PSU
                event.exec(PSUList[event.PSUidx])
            else:
                event.exec()

        elif isinstance(event, BoolEvent): # Events that return bool...
            if isinstance(event, BoolPSUEvent): # ...and use a PSU
                logging.info("PASS" if event.exec(PSUList[event.PSUidx]) else "FAIL")
            else:
                logging.info("PASS" if event.exec() else "FAIL")

        else:
            raise ValueError(f"Invalid Event type: {type(event)}")

def _shutdown(shutdownOrder: list[int], PSUList: list[PowerSupply]):

    if not shutdownOrder:
        logging.info(f"Empty shutdownOrder, defaulting to ascending order.")
        orderedPSUList = PSUList
        indexList = [i for i, _ in enumerate(PSUList)]

    elif ( set(shutdownOrder) != set(range(len(PSUList))) ): # If the shutdownOrder does not include each PSU index
        logging.warning(f"Invalid shutdownOrder (does not include every PSU index), defaulting to ascending order.")
        orderedPSUList = PSUList
        indexList = [i for i, _ in enumerate(PSUList)]

    elif ( len(shutdownOrder) != len(set(shutdownOrder)) ): # If the shutdownOrder has duplicate indices
        logging.warning(f"Invalid shutdownOrder (duplicate indices), defaulting to ascending order.")
        orderedPSUList = PSUList
        indexList = [i for i, _ in enumerate(PSUList)]

    else:
        orderedPSUList = [PSUList[i] for i in shutdownOrder]
        indexList = shutdownOrder

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
