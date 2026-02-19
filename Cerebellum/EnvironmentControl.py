"""
EnvironmentControl.py
This file contains the EnvironmentControl library, which is used to send
commands and receive data from the devices of the test environment. The primary
function is runTest, which executes the test specified by a TestSettings object
on the test environment specified by an EnvironmentConfig object.

This file also contains several helper classes and functions.
TODO: add CC/CV command to _PSU
TODO: implement CC/CV in runTest
TODO: implement enable/disable in runTest
"""

from EnvironmentConfig import EnvironmentConfig, PSUConfig
from TestSettings import TestSettings, Criterion
import serial, socketscpi, time, re

SCPI_WRITE_DELAY = 0.1

def runTest(config: EnvironmentConfig, settings: TestSettings):
    
    # Initialize all PSUs 
    print("Intializing PSUs ==========")
    PSUList = []
    for idx, psu in enumerate(config.PSUConfigList):
        print(f"Initializing PSU #{idx} -----")
        PSUList.append(_PSU(psu))

    # Report and wait for user input
    print()
    print("All PSUs initialized successfully.")
    print("Verify the credentials appear as expected before continuing. (Next step: Setting PSUs to assigned levels)")
    input("Press Enter to continue...")
    print()

    # Set all PSUs to their assigned settings
    print("Setting PSUs to assigned levels ==========")
    for idx, (psu, setting) in enumerate(zip(PSUList, settings.PSUSettingsList)):
        print(f"Initializing PSU #{idx} -----")
        print(f"Voltage: {setting.voltage}")
        print(f"Current: {setting.current}")
        psu.turnOff()
        psu.setVoltage(setting.voltage)
        psu.setCurrent(setting.current)
    
    # Report and wait for user input
    print()
    print("All PSUs set successfully.")
    print("Verify the settings appear as expected before continuing. (Next step: Enabling PSUs)")
    input("Press Enter to continue...")
    print()

    # Turn on all PSUs
    for idx, psu in enumerate(PSUList):
        print(f"Enabling PSU #{idx} -----")
        psu.turnOn()

    # Report and wait for user input
    print()
    print("All PSUs enabled successfully.")
    print("Verify the PSUs are behaving as expected before continuing. (Next step: Checking criteria)")
    input("Press Enter to continue...")
    print()

    # Check all criteria


"""
Power Supply Control ===========================================================
"""
class _PSU:

    # Initialize connection, verify with ID and version query
    def __init__(self, config: PSUConfig):

        self.config = config

        if (self.config.protocol == "Serial"):
            try:
                self.ser = serial.Serial(
                    port=self.config.COM,
                    baudrate=self.config.baudrate,
                    timeout=1.0
                )
                print(f"Opened serial port {self.config.COM}.")
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
            except serial.SerialException as e:
                raise RuntimeError(f"Failed to open serial port {self.config.COM}: {e}")
        elif (self.config.protocol == "IP"):
            try:
                self.socket = socketscpi.SocketInstrument(self.config.IP)
            except socketscpi.SockInstError as e:
                raise RuntimeError(f"Failed to open IP socket {self.config.IP}: {e}")
        else:
            raise ValueError(f"Invalid protocol value: {self.config.protocol}")
        
        print(f"IDN: {self.getIDN()}")
        print(f"Version: {self.getVersion()}")
    
    # Attempt to close any open connections
    def __del__(self):
        if ("ser" in vars(self)) and self.ser and self.ser.is_open:
            self.ser.close()
            print(f"Closed serial port {self.config.COM}.")
        if ("socket" in vars(self)) and self.socket:
            self.socket.close()
            print(f"Closed IP socket {self.config.IP}.")

    # Send an SCPI command and return the decoded response
    # Pass to _parseFloatSCPI to extract float
    def _querySCPI(self, cmd: str):

        if (self.config.protocol == "Serial"):
            if not self.ser or not self.ser.is_open:
                raise RuntimeError(f"Serial port {self.config.COM} is not open.")
            self.ser.reset_input_buffer()
            self.ser.write(cmd.encode())
            self.ser.flush()
            time.sleep(SCPI_WRITE_DELAY)
            response = self.ser.readline()
            try:
                return response.decode().strip() if response else ""
            except UnicodeDecodeError:
                print("Unreadable response: ", response)
                return ""
        elif (self.config.protocol == "IP"):
            if not self.socket:
                raise RuntimeError(f"IP socket {self.config.IP} is not open.")
            return self.socket.query(cmd)
        return ""
    
    # Send an SCPI command without reading a response
    def _writeSCPI(self, cmd: str):

        if (self.config.protocol == "Serial"):
            if not self.ser or not self.ser.is_open:
                raise RuntimeError(f"Serial port {self.config.COM} is not open.")
            self.ser.reset_input_buffer()
            self.ser.write(cmd.encode())
            self.ser.flush()
        elif (self.config.protocol == "IP"):
            if not self.socket:
                raise RuntimeError(f"IP socket {self.config.IP} is not open.")
            self.socket.write(cmd)

        time.sleep(SCPI_WRITE_DELAY)
    
    """
    PSU control commands ==========
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
            self._writeSCPI(f"VOLT {voltage}\n")

    def setCurrent(self, current: float):
        if (self.config.interface == "SCPI"):
            self._writeSCPI(f"INST:SEL {self.config.channel}\n")
            self._writeSCPI(f"CURR {current}\n")
    
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



# Extract a float (e.g. voltage) from a decoded SCPI response
def _parseFloatSCPI(response: str):
    match = re.search(r"[-+]?\d*\.?\d+", response)
    return float(match.group(0)) if match else None



"""
Criterion Evaluation ===========================================================
"""

#def _evalPSUVoltage(criterion: Criterion, psu: _PSU):

