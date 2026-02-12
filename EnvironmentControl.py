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

#def runTest(config: EnvironmentConfig, settings: TestSettings):




class _PSU:

    """
    Initialize connection, verify with ID and version query
    """
    def __init__(self, config: PSUConfig):

        self.config = config

        if (self.config.connector == "USB"):
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

    """
    Send an SCPI command and return the decoded response
    Pass to _parseFloatSCPI to extract float
    """
    def _querySCPI(self, cmd: str, delay: float = 0.1):

        if (self.config.connector == "USB"):
            if not self.ser or not self.ser.is_open:
                raise RuntimeError(f"Serial port {self.config.COM} is not open.")
            self.ser.reset_input_buffer()
            self.ser.write(cmd.encode())
            self.ser.flush()
            time.sleep(delay)
            response = self.ser.readline()
            try:
                return response.decode().strip() if response else None
            except UnicodeDecodeError:
                print("Unreadable response: ", response)
                return None
    
    """
    Send an SCPI command without reading a response
    """
    def _writeSCPI(self, cmd: str, delay: float = 0.1):
        if (self.config.connector == "USB"):
            if not self.ser or not self.ser.is_open:
                raise RuntimeError(f"Serial port {self.config.COM} is not open.")
            self.ser.reset_input_buffer()
            self.ser.write(cmd.encode())
            self.ser.flush()
            time.sleep(delay)
    
    """
    Commands
    """
    def getIDN(self):
        return self._querySCPI("*IDN?\n")
    
    def getVersion(self):
        return self._querySCPI("SYST:VERS?\n")
    
    def setVoltage(self, voltage: float):
        self._writeSCPI(f"INST:SEL {self.config.channel}\n")
        self._writeSCPI(f"VOLT {voltage:.2f}V\n")




"""
Extract a float (e.g. V or A) from a decoded SCPI response
"""
def _parseFloatSCPI(response: str):
    match = re.search(r"[-+]?\d*\.?\d+", response)
    return float(match.group(0)) if match else None
