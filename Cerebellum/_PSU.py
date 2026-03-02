"""
_PSU.py
This file contains the _PSU class, which is used to translate high-level PSU
commands into protocol and interface-specific commands. Primarily used by
EnvironmentControl.
"""

from EnvironmentConfig import PSUConfig
import serial, socketscpi, time, re

SCPI_WRITE_DELAY = 0.1



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
    
    # Attempt to close any open connections when deallocated
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
        else:
            raise ValueError(f"Invalid protocol value: {self.config.protocol}")
    
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
        else:
            raise ValueError(f"Invalid protocol value: {self.config.protocol}")

        time.sleep(SCPI_WRITE_DELAY)

    """
    PSU control commands ==========
    """
    def getIDN(self):
        if (self.config.interface == "SCPI"):
            return self._querySCPI("*IDN?\n")
        else:
            raise ValueError(f"Invalid interface value: {self.config.interface}")

    def getVersion(self):
        if (self.config.interface == "SCPI"):
            return self._querySCPI("SYST:VERS?\n")
        else:
            raise ValueError(f"Invalid interface value: {self.config.interface}")

    def setVoltage(self, voltage: float):
        if (self.config.interface == "SCPI"):
            self._writeSCPI(f"INST:SEL {self.config.channel}\n")
            self._writeSCPI(f"VOLT {voltage}\n")
        else:
            raise ValueError(f"Invalid interface value: {self.config.interface}")

    def setCurrent(self, current: float):
        if (self.config.interface == "SCPI"):
            self._writeSCPI(f"INST:SEL {self.config.channel}\n")
            self._writeSCPI(f"CURR {current}\n")
        else:
            raise ValueError(f"Invalid interface value: {self.config.interface}")

    def getVoltage(self):
        if (self.config.interface == "SCPI"):
            self._writeSCPI(f"INST:SEL {self.config.channel}\n")
            return _parseFloatSCPI(self._querySCPI("VOLT?\n"))
        else:
            raise ValueError(f"Invalid interface value: {self.config.interface}")

    def getCurrent(self):
        if (self.config.interface == "SCPI"):
            self._writeSCPI(f"INST:SEL {self.config.channel}\n")
            return _parseFloatSCPI(self._querySCPI("CURR?\n"))
        else:
            raise ValueError(f"Invalid interface value: {self.config.interface}")

    def measureVoltage(self):
        if (self.config.interface == "SCPI"):
            self._writeSCPI(f"INST:SEL {self.config.channel}\n")
            return _parseFloatSCPI(self._querySCPI("MEAS:VOLT?\n"))
        else:
            raise ValueError(f"Invalid interface value: {self.config.interface}")

    def measureCurrent(self):
        if (self.config.interface == "SCPI"):
            self._writeSCPI(f"INST:SEL {self.config.channel}\n")
            return _parseFloatSCPI(self._querySCPI("MEAS:CURR?\n"))
        else:
            raise ValueError(f"Invalid interface value: {self.config.interface}")

    def turnOff(self):
        if (self.config.interface == "SCPI"):
            self._writeSCPI(f"INST:SEL {self.config.channel}\n")
            self._writeSCPI(f"OUTP:STAT 0\n")
        else:
            raise ValueError(f"Invalid interface value: {self.config.interface}")

    def turnOn(self):
        if (self.config.interface == "SCPI"):
            self._writeSCPI(f"INST:SEL {self.config.channel}\n")
            self._writeSCPI(f"OUTP:STAT 1\n")
        else:
            raise ValueError(f"Invalid interface value: {self.config.interface}")



# Extract a float (e.g. voltage) from a decoded SCPI response
def _parseFloatSCPI(response: str):
    match = re.search(r"[-+]?\d*\.?\d+", response)
    if not match:
        raise RuntimeError(f"Unable to locate value in response: {response}")
    return float(match.group(0))
