"""
EnvironmentControl.py
This file contains the EnvironmentControl library, which is used to send
commands and receive data from the devices of the test environment. The primary
function is run_test, which executes the test specified by a TestConfig object
on the test environment specified by an EnvironmentConfig object.

This file also contains several helper classes and functions.
"""

# Prevents TypeError on type hints for Python 3.7 to 3.9
from __future__ import annotations

from Cerebellum.Common import create_device
from Cerebellum.InputProcessing import stdin_listener, stop_event, get_input
from Cerebellum.EnvironmentConfig import EnvironmentConfig
from Cerebellum.TestConfig import TestConfig
from Cerebellum.Event import Event, DeviceEvent, DeferredInitEvent
from Cerebellum.Device.Device import Device, DeviceConfig

import logging, threading, signal
from contextlib import contextmanager

threading.Thread(target=stdin_listener, daemon=True).start()



"""
Main Function + Helpers ========================================================
"""

def run_test(env: EnvironmentConfig, test: TestConfig) -> None:
    
    # Attempt to run the regular program sequence
    try:
        
        # Before anything, check that each DeviceEvent will refer to a device that exists and matches the type (e.g. PowerSupplyEvent)
        # Also build a list of device idx that will defer their inits
        logging.info("Verifying event list ==========")
        deferred_devices: list[int] = []
        for idx, event in enumerate(test.event_list):
            if isinstance(event, DeviceEvent):

                try:
                    _ = env.device_config_list[event.device_idx]
                except IndexError:
                    raise IndexError(f"Event #{idx} failed to verify: device_idx ({event.device_idx}) is out of range of the device list.")
                
                try:
                    event.verify(env.device_config_list[event.device_idx])
                except Exception as e:
                    raise RuntimeError(f"Event #{idx} failed to verify: {e}")

                if isinstance(event, DeferredInitEvent):
                    deferred_devices.append(event.device_idx)
                
        logging.info("All events verified successfully.")

        # Initialize all devices
        logging.info("Intializing devices ==========")
        if deferred_devices:
            logging.info(f"Devices with deferred initialization will be skipped: {deferred_devices}")
        device_list = _init_device_list(env.device_config_list, deferred_devices)

        # Report and wait for user input
        logging.info("All devices initialized successfully.")
        logging.info("Verify the credentials appear as expected before continuing to event execution.")
        get_input("Press Enter to continue...")

        # Execute all events
        logging.info("")
        logging.info("Executing events ==========")
        _exec_events(test.event_list, device_list, env.device_config_list)

        # Report and wait for user input
        logging.info("")
        logging.info("All events exeucted successfully.")
    
    # If there are any errors in normal operation, skip to disabling the devices
    # Block all external interrupts while doing so, and keep disabling the other
    # devices even if one of them fails
    # A standard Exception will end run_test prematurely
    # A BaseException (e.g. KeyboardInterrupt) will end the entire program
    except Exception as e:

        print()
        logging.basicConfig(format="%(levelname)s: %(message)s", force=True)
        logging.error(f"During the testing routine, an exception was encountered: {e}")
        logging.error(f"Aborting testing routine.")
        pass

    finally:
        with _DelayedInterrupt([signal.SIGINT, signal.SIGTERM]):

            # If device_list has been initialized, shutdown all devices
            if "device_list" not in locals():
                logging.info("Device list has not been initialized. Skipping shutdown sequence.")
            else:
                logging.info("Shutting down devices ==========")
                _shutdown(env.shutdown_order, device_list)



def _init_device_list(device_config_list: list[DeviceConfig], deferred_devices: list[int]) -> list[Device]:
    
    device_list = []
    for idx, device_config in enumerate(device_config_list):
        if idx in deferred_devices:
            # Append None for now to reserve the position of the device to be initialized later
            device_list.append(None)
        else:
            logging.info(f"Initializing device #{idx} ({device_config.display_name}) ----------")
            with tab_logging():
                device_list.append(create_device(device_config))
        
    return device_list



def _exec_events(event_list: list[Event], device_list: list[Device], device_config_list: list[DeviceConfig]) -> None:

    for idx, event in enumerate(event_list):

        # Check if the message "STOP" is sent on stdin before running the next event in the loop
        # If so, throw a RuntimeError
        if stop_event.is_set():
            raise RuntimeError("Received message on stdin to abort the testing routine.")

        logging.info(f"Executing event #{idx} ----------")
        with tab_logging():
            logging.info(f"{event.__class__.__name__}: {event.comment}")

            if isinstance(event, DeferredInitEvent):
                logging.info(f"Initializing device #{event.device_idx} ({device_config_list[event.device_idx].display_name})")
                device_list[event.device_idx] = create_device(device_config_list[event.device_idx])
            elif isinstance(event, DeviceEvent):
                device = device_list[event.device_idx]
                if device:
                    event.exec(device_list[event.device_idx])
                else:
                    raise RuntimeError(f"Device #{event.device_idx} ({device_config_list[event.device_idx].display_name}) was not initialized before use. Check if a DeferredInitEvent is called before this event.")
            else:
                event.exec()



def _shutdown(shutdown_order: list[int], device_list: list[Device]):

    # Create final_order, which is [shutdown_order, {rest of device indices, ascending}]
    ascending_order = [dev_idx for dev_idx in list(range(len(device_list))) if dev_idx not in shutdown_order]
    final_order = shutdown_order + ascending_order

    # Shutdown the devices according to final_order
    for dev_idx in final_order:
        try:
            device = device_list[dev_idx]
            logging.info(f"Disabling device #{dev_idx} ({device.config.display_name}) -----")
            device.shutdown()
        except Exception as e:
            logging.error(f"While attemping to disable device #{dev_idx}, an exception was encountered: {e}")
            pass



# Simple contextmanager to tab logging format during an event
@contextmanager
def tab_logging():

    # Tab four spaces
    logging.basicConfig(format="%(levelname)s:     %(message)s", force=True)

    yield
    
    # Return formatting to default
    logging.basicConfig(format="%(levelname)s: %(message)s", force=True)



# Interrupt Delayer
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
