"""
SCPIPowerSupply.py
This file contains the SCPIPowerSupply class, which is an implementation of the
PowerSupply interface for an SCPI-programmable power supply. This implementation
supports control over a serial/USB or IP connection.
"""

# Prevents TypeError on type hints for Python 3.7 to 3.9
from __future__ import annotations

from Cerebellum.Device.PowerSupply import PowerSupply, PowerSupplyConfig

from typing import Any
import serial, socketscpi, time, re, logging

SCPI_WRITE_DELAY = 0.1



class SCPIPowerSupplyConfig(PowerSupplyConfig):

    # *_title = String to show as field title in GUI (e.g. COM Port: _____)
    # Any field without a corresponding field_title will default to the field name
    protocol_title      = "Protocol"
    ip_title            = "IP Address"
    com_title           = "COM Port"
    baudrate_title      = "Baudrate"
    
    # *_options = Options for field to provide in a dropdown menu
    # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type
    protocol_options    = ["IP", "Serial"]
    baudrate_options    = [2400, 4800, 9600, 19200, 38400, 57600, 115200]

    # Either init with default values or init with input fields (read from JSON)
    def __init__(self, vars_dict: dict[str, Any] = {}):
        if vars_dict:
            vars(self).update(vars_dict) # Install input into __dict__
        else:
            self.display_name   : str   = "SCPI Power Supply"       # Display name of the power supply
            self.protocol       : str   = "IP"                      # Communication protocol (IP / Serial)
            self.ip             : str   = ""                        # IP address
            self.com            : str   = ""                        # COM port (e.g. /dev/ttyACM0, COM1)
            self.baudrate       : int   = 115200                    # COM baudrate



class SCPIPowerSupply(PowerSupply):

    """
    Interface Methods ======================================================
    """

    # Initialize connection, possibly log ID
    def __init__(self, config: SCPIPowerSupplyConfig):

        self.config = config

        if (self.config.protocol == "Serial"):
            try:
                self.ser = serial.Serial(
                    port=self.config.com,
                    baudrate=self.config.baudrate
                )
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                logging.info(f"Opened SCPIPowerSupply at serial port ({self.config.com}).")
            except Exception as e:
                raise RuntimeError(f"Failed to open SCPIPowerSupply at serial port ({self.config.com}): {e}")
        elif (self.config.protocol == "IP"):
            try:
                self.socket = socketscpi.SocketInstrument(self.config.ip)
                logging.info(f"Opened SCPIPowerSupply at IP address ({self.config.ip}).")
            except Exception as e:
                raise RuntimeError(f"Failed to open SCPIPowerSupply at IP address ({self.config.ip}): {e}")
        else:
            raise ValueError(f"Invalid protocol value: {self.config.protocol}")

    # Attempt to close any open connections when deallocated
    def __del__(self):
        if ("ser" in vars(self)) and self.ser and self.ser.is_open:
            self.ser.close()
            logging.info(f"Closed SCPIPowerSupply at serial port ({self.config.com}).")
        if ("socket" in vars(self)) and self.socket:
            self.socket.close()
            logging.info(f"Closed SCPIPowerSupply at IP address ({self.config.ip}).")
    
    # Get any identification data
    def get_id(self) -> str:
        idn = self._query_scpi("*IDN?\n")
        vers = self._query_scpi("SYST:VERS?\n")
        return f"IDN: {idn}, SCPI Version: {vers}"

    # Set the voltage setting of the given channel
    def set_voltage(self, channel: int, voltage: float) -> None:
        self._write_scpi(f"INST:SEL {channel}\n")
        self._write_scpi(f"VOLT {voltage}\n")

    # Set the current setting of the given channel
    def set_current(self, channel: int, current: float) -> None:
        self._write_scpi(f"INST:SEL {channel}\n")
        self._write_scpi(f"CURR {current}\n")

    # Get the voltage setting of the given channel
    def get_voltage(self, channel: int) -> float:
        self._write_scpi(f"INST:SEL {channel}\n")
        return self._parse_float_scpi(self._query_scpi("VOLT?\n"))

    # Get the current setting of the given channel
    def get_current(self, channel: int) -> float:
        self._write_scpi(f"INST:SEL {channel}\n")
        return self._parse_float_scpi(self._query_scpi("CURR?\n"))
    
    # Measure the voltage at the given channel
    def measure_voltage(self, channel: int) -> float:
        self._write_scpi(f"INST:SEL {channel}\n")
        return self._parse_float_scpi(self._query_scpi("MEAS:VOLT?\n"))
    
    # Measure the current at the given channel
    def measure_current(self, channel: int) -> float:
        self._write_scpi(f"INST:SEL {channel}\n")
        return self._parse_float_scpi(self._query_scpi("MEAS:CURR?\n"))
    
    # Measure the power at the given channel
    def measure_power(self, channel: int) -> float:
        self._write_scpi(f"INST:SEL {channel}\n")
        return self._parse_float_scpi(self._query_scpi("MEAS:POW?\n"))
    
    # Disable the given channel
    def disable_channel(self, channel: int) -> None:
        self._write_scpi(f"INST:SEL {channel}\n")
        self._write_scpi(f"OUTP:STAT 0\n")
    
    # Enable the given channel
    def enable_channel(self, channel: int) -> None:
        self._write_scpi(f"INST:SEL {channel}\n")
        self._write_scpi(f"OUTP:STAT 1\n")

    # Return the enable/disable state of the given channel
    def get_channel_state(self, channel: int) -> bool:
        self._write_scpi(f"INST:SEL {channel}\n")
        return bool(int(self._query_scpi(f"OUTP:STAT?\n")))
    
    # Shutdown (i.e. disable, not disconnect) the device
    def shutdown(self) -> None:
        self._write_scpi(f"OUTP:ALL 0\n")
        time.sleep(5)



    """
    Helper Methods =========================================================
    """

    # Send an SCPI command without reading a response
    def _write_scpi(self, cmd: str) -> None:

        if (self.config.protocol == "Serial"):
            if not self.ser or not self.ser.is_open:
                raise RuntimeError(f"Serial port {self.config.com} is not open.")
            self.ser.reset_input_buffer()
            self.ser.write(cmd.encode())
            self.ser.flush()
        elif (self.config.protocol == "IP"):
            if not self.socket:
                raise RuntimeError(f"IP address {self.config.ip} is not open.")
            self.socket.write(cmd)
        else:
            raise ValueError(f"Invalid protocol value: {self.config.protocol}")

        time.sleep(SCPI_WRITE_DELAY)

    # Send an SCPI command and return the decoded response
    # Pass to _parse_float_scpi to extract float
    def _query_scpi(self, cmd: str) -> str:

        if (self.config.protocol == "Serial"):
            if not self.ser or not self.ser.is_open:
                raise RuntimeError(f"Serial port {self.config.com} is not open.")
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
                raise RuntimeError(f"IP address {self.config.ip} is not open.")
            return self.socket.query(cmd)
        else:
            raise ValueError(f"Invalid protocol value: {self.config.protocol}")

    # Extract a float (e.g. voltage) from a decoded SCPI response
    @staticmethod
    def _parse_float_scpi(response: str) -> float:
        match = re.search(r"[-+]?\d*\.?\d+", response)
        if not match:
            raise RuntimeError(f"Unable to locate value in response: {response}")
        return float(match.group(0))
