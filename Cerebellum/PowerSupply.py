"""
PowerSupply.py
This file contains the PowerSupply interface, which specifies the high-level
commands that EnvironmentControl will use.

This file also contains SCPIPowerSupply, which is an implementation of the
PowerSupply interface for an SCPI-controlled power supply, either over an IP
or a Serial connection.

Lastly, this file contains a factory function that will instantiate the correct
object based on the input PSUConfig. For example, a config with an SCPI
interface will be constructed as an SCPIPowerSupply.
"""

# Always make sure that Cerebellum and its submodules are on the import path
import sys, os
sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Cerebellum.EnvironmentConfig import PSUConfig

from abc import ABC, abstractmethod
import importlib

import serial, socketscpi, time, re, logging
logging.basicConfig(level=logging.INFO)

SCPI_WRITE_DELAY = 0.1



class PowerSupply(ABC):

    config  : PSUConfig # Configuration of this power supply

    """
    Interface Methods ======================================================
    """

    # Initialize connection, possibly log ID
    @abstractmethod
    def __init__(self, config: PSUConfig):
        pass

    # Attempt to close any open connections when deallocated
    @abstractmethod
    def __del__(self):
        pass
    
    # Get any identification data
    @abstractmethod
    def getID(self) -> str:
        pass

    # Set the voltage setting of the given channel
    @abstractmethod
    def setVoltage(self, channel: int, voltage: float) -> None:
        pass

    # Set the current setting of the given channel
    @abstractmethod
    def setCurrent(self, channel: int, current: float) -> None:
        pass

    # Get the voltage setting of the given channel
    @abstractmethod
    def getVoltage(self, channel: int) -> float:
        pass

    # Get the current setting of the given channel
    @abstractmethod
    def getCurrent(self, channel: int) -> float:
        pass
    
    # Measure the voltage at the given channel
    @abstractmethod
    def measureVoltage(self, channel: int) -> float:
        pass
    
    # Measure the current at the given channel
    @abstractmethod
    def measureCurrent(self, channel: int) -> float:
        pass

    # Measure the power at the given channel
    @abstractmethod
    def measurePower(self, channel: int) -> float:
        pass
    
    # Disable the given channel
    @abstractmethod
    def disableChannel(self, channel: int) -> None:
        pass
    
    # Enable the given channel
    @abstractmethod
    def enableChannel(self, channel: int) -> None:
        pass

    # Return the enable/disable state of the given channel
    @abstractmethod
    def getChannelState(self, channel: int) -> bool:
        pass
    
    # Shutdown all channels
    @abstractmethod
    def shutdown(self) -> None:
        pass



class SCPIPowerSupply(PowerSupply):

    config  : PSUConfig                     # Configuration of this power supply
    ser     : serial.Serial                 # Serial object (for COM)
    socket  : socketscpi.SocketInstrument   # Socket object (for IP)

    """
    Interface Methods ======================================================
    """

    # Initialize connection, possibly log ID
    def __init__(self, config: PSUConfig):

        self.config = config

        if (self.config.protocol == "Serial"):
            try:
                self.ser = serial.Serial(
                    port=self.config.COM,
                    baudrate=self.config.baudrate
                )
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                logging.info(f"Opened SCPIPowerSupply at serial port ({self.config.COM}).")
            except serial.SerialException as e:
                raise RuntimeError(f"Failed to open SCPIPowerSupply at serial port ({self.config.COM}): {e}")
        elif (self.config.protocol == "IP"):
            try:
                self.socket = socketscpi.SocketInstrument(self.config.IP)
                logging.info(f"Opened SCPIPowerSupply at IP socket ({self.config.IP}).")
            except socketscpi.SockInstError as e:
                raise RuntimeError(f"Failed to open SCPIPowerSupply at IP socket ({self.config.IP}): {e}")
        else:
            raise ValueError(f"Invalid protocol value: {self.config.protocol}")
        
        logging.info(self.getID())

    # Attempt to close any open connections when deallocated
    def __del__(self):
        if ("ser" in vars(self)) and self.ser and self.ser.is_open:
            self.ser.close()
            logging.info(f"Closed SCPIPowerSupply at serial port ({self.config.COM}).")
        if ("socket" in vars(self)) and self.socket:
            self.socket.close()
            logging.info(f"Closed SCPIPowerSupply at IP socket ({self.config.IP}).")
    
    # Get any identification data
    def getID(self) -> str:
        IDN = self._querySCPI("*IDN?\n")
        VERS = self._querySCPI("SYST:VERS?\n")
        return f"IDN: {IDN}, SCPI Version: {VERS}"

    # Set the voltage setting of the given channel
    def setVoltage(self, channel: int, voltage: float) -> None:
        self._writeSCPI(f"INST:SEL {channel}\n")
        self._writeSCPI(f"VOLT {voltage}\n")

    # Set the current setting of the given channel
    def setCurrent(self, channel: int, current: float) -> None:
        self._writeSCPI(f"INST:SEL {channel}\n")
        self._writeSCPI(f"CURR {current}\n")

    # Get the voltage setting of the given channel
    def getVoltage(self, channel: int) -> float:
        self._writeSCPI(f"INST:SEL {channel}\n")
        return self._parseFloatSCPI(self._querySCPI("VOLT?\n"))

    # Get the current setting of the given channel
    def getCurrent(self, channel: int) -> float:
        self._writeSCPI(f"INST:SEL {channel}\n")
        return self._parseFloatSCPI(self._querySCPI("CURR?\n"))
    
    # Measure the voltage at the given channel
    def measureVoltage(self, channel: int) -> float:
        self._writeSCPI(f"INST:SEL {channel}\n")
        return self._parseFloatSCPI(self._querySCPI("MEAS:VOLT?\n"))
    
    # Measure the current at the given channel
    def measureCurrent(self, channel: int) -> float:
        self._writeSCPI(f"INST:SEL {channel}\n")
        return self._parseFloatSCPI(self._querySCPI("MEAS:CURR?\n"))
    
    # Measure the power at the given channel
    def measurePower(self, channel: int) -> float:
        self._writeSCPI(f"INST:SEL {channel}\n")
        return self._parseFloatSCPI(self._querySCPI("MEAS:POW?\n"))
    
    # Disable the given channel
    def disableChannel(self, channel: int) -> None:
        self._writeSCPI(f"INST:SEL {channel}\n")
        self._writeSCPI(f"OUTP:STAT 0\n")
    
    # Enable the given channel
    def enableChannel(self, channel: int) -> None:
        self._writeSCPI(f"INST:SEL {channel}\n")
        self._writeSCPI(f"OUTP:STAT 1\n")

    # Return the enable/disable state of the given channel
    def getChannelState(self, channel: int) -> bool:
        self._writeSCPI(f"INST:SEL {channel}\n")
        return bool(self._querySCPI(f"OUTP:STAT?\n"))
    
    # Shutdown all channels
    def shutdown(self) -> None:
        self._writeSCPI(f"OUTP:ALL 0\n")



    """
    Helper Methods =========================================================
    """

    # Send an SCPI command without reading a response
    def _writeSCPI(self, cmd: str) -> None:

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

    # Send an SCPI command and return the decoded response
    # Pass to _parseFloatSCPI to extract float
    def _querySCPI(self, cmd: str) -> str:

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
                logging.warning(f"Unreadable response: {response}")
                return ""
        elif (self.config.protocol == "IP"):
            if not self.socket:
                raise RuntimeError(f"IP socket {self.config.IP} is not open.")
            return self.socket.query(cmd)
        else:
            raise ValueError(f"Invalid protocol value: {self.config.protocol}")

    # Extract a float (e.g. voltage) from a decoded SCPI response
    @staticmethod
    def _parseFloatSCPI(response: str) -> float:
        match = re.search(r"[-+]?\d*\.?\d+", response)
        if not match:
            raise RuntimeError(f"Unable to locate value in response: {response}")
        return float(match.group(0))



def createPowerSupply(config: PSUConfig) -> PowerSupply:
    if (config.interface == "SCPI"):
        return SCPIPowerSupply(config)
    elif (config.interface == "Custom"):
        # Assumed that the module and class have the same name
        module = importlib.import_module(config.implementation)
        constructor = getattr(module, config.implementation)
        return constructor(config)
    else:
        raise ValueError(f"Invalid interface value: {config.interface}")
