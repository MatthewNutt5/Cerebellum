"""
EnvironmentControl.py
This file contains the EnvironmentControl library, which is used to send
commands and receive data from the devices of the test environment. The primary
function is runTest, which executes the test specified by a TestSettings object
on the test environment specified by an EnvironmentConfig object.

This file also contains several helper classes and functions.
"""

from EnvironmentConfig import EnvironmentConfig, PSUConfig
from TestSettings import TestSettings, Criterion
import serial, time, re

SERIAL_WRITE_DELAY = 0.1

#def runTest(config: EnvironmentConfig, settings: TestSettings):



class _PSU:

    """
    Initialize connection, verify with ID and version query
    """
    def __init__(self, config: PSUConfig):

        self.config = config

        if (self.config.protocol == "Serial"):
            try:
                self.ser = serial.Serial(
                    port=self.config.COM,
                    baudrate=self.config.baudrate,
                    timeout=1.0
                )
                time.sleep(2)  # Wait for connection to establish
                print(f"Connected to {self.config.COM}")
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
            except serial.SerialException as e:
                raise RuntimeError(f"Failed to open serial port {self.config.COM}: {e}")
        
        print(f"ID: {self.getIDN()}")
        print(f"Version: {self.getVersion()}")
    
    def __del__(self):
        # Attempt to close any COM connections
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"Closed serial port {self.config.COM}.")

    """
    Send an SCPI command and return the decoded response
    Pass to _parseFloatSCPI to extract float
    """
    def _querySCPI(self, cmd: str):

        if (self.config.protocol == "Serial"):
            if not self.ser or not self.ser.is_open:
                raise RuntimeError(f"Serial port {self.config.COM} is not open.")
            self.ser.reset_input_buffer()
            self.ser.write(cmd.encode())
            self.ser.flush()
            time.sleep(SERIAL_WRITE_DELAY)
            response = self.ser.readline()
            try:
                return response.decode().strip() if response else ""
            except UnicodeDecodeError:
                print("Unreadable response: ", response)
                return ""
        return ""
    
    """
    Send an SCPI command without reading a response
    """
    def _writeSCPI(self, cmd: str):

        if (self.config.protocol == "Serial"):
            if not self.ser or not self.ser.is_open:
                raise RuntimeError(f"Serial port {self.config.COM} is not open.")
            self.ser.reset_input_buffer()
            self.ser.write(cmd.encode())
            self.ser.flush()
            time.sleep(SERIAL_WRITE_DELAY)
    
    """
    PSU control commands =======================================================
    """
    def getIDN(self):
        if (self.config.interface == "SCPI"):
            return self._querySCPI("*IDN?\n")
    
    def getVersion(self):
        if (self.config.interface == "SCPI"):
            return self._querySCPI("SYST:VERS?\n")
    
    def setVoltage(self, voltage: float):
        if (self.config.interface == "SCPI"):
            self._writeSCPI(f"INST:SEL {self.config.channel}\n")
            self._writeSCPI(f"VOLT {voltage:.3f}\n")

    def setCurrent(self, current: float):
        if (self.config.interface == "SCPI"):
            self._writeSCPI(f"INST:SEL {self.config.channel}\n")
            self._writeSCPI(f"CURR {current:.3f}\n")
    
    def measureVoltage(self):
        if (self.config.interface == "SCPI"):
            self._writeSCPI(f"INST:SEL {self.config.channel}\n")
            return _parseFloatSCPI(self._querySCPI("MEAS:VOLT?\n"))

    def measureCurrent(self):
        if (self.config.interface == "SCPI"):
            self._writeSCPI(f"INST:SEL {self.config.channel}\n")
            return _parseFloatSCPI(self._querySCPI("MEAS:CURR?\n"))
        
    def turnOff(self):
        if (self.config.interface == "SCPI"):
            self._writeSCPI(f"INST:SEL {self.config.channel}\n")
            self._writeSCPI(f"OUTP:STAT 0\n")

    def turnOn(self):
        if (self.config.interface == "SCPI"):
            self._writeSCPI(f"INST:SEL {self.config.channel}\n")
            self._writeSCPI(f"OUTP:STAT 1\n")


"""
Extract a float (e.g. voltage) from a decoded SCPI response
"""
def _parseFloatSCPI(response: str):
    match = re.search(r"[-+]?\d*\.?\d+", response)
    return float(match.group(0)) if match else None
