"""
Placeholder
"""

from Cerebellum.Device.Device import Device, DeviceConfig

import time, random
from typing import Any
from tamalero.ReadoutBoard import ReadoutBoard
from tamalero.utils import get_kcu



class TamaleroReadoutBoardConfig(DeviceConfig):
    
    # *_title = String to show as field title in GUI (e.g. COM Port: _____)
    # Any field without a corresponding field_title will default to the field name
    kcu_address_title   : str = "KCU IP Address"
    host_title          : str = "Control Hub Host"
    rb_index_title      : str = "Readout Board Index"
    flavor_title        : str = "Board Flavor"
    configuration_title : str = "Configuration"
    etroc_title         : str = "ETROC Version"

    # *_options = Options for field to provide in a dropdown menu
    # Any field without a corresponding field_options will default to a text box/spin box/toggle, depending on the type
    flavor_options          : list[str] = ['small', 'medium', 'large']
    configuration_options   : list[str] = ['default', 'emulator', 'modulev0', 'modulev0b', 'multimodule', 'mux64', 'modulev1', 'modulev2']
    etroc_options           : list[str] = ['ETROC1', 'ETROC2']

    # Either init with default values or init with input fields (read from JSON)
    def __init__(self, vars_dict: dict[str, Any] = {}):
        if vars_dict:
            vars(self).update(vars_dict)
        else:
            self.display_name   : str = "Tamalero Readout Board"
            self.kcu_address    : str = ""
            self.host           : str = "localhost"
            self.rb_index       : int = 0
            self.flavor         : str = "small"
            self.configuration  : str = "default"
            self.etroc          : str = "ETROC2"



class TamaleroReadoutBoard(Device):

    """
    Interface Methods ======================================================
    """
    
    # Initialize connection, possibly log ID
    def __init__(self, config: TamaleroReadoutBoardConfig):

        self.config = config

        # Try to connect to KCU (FPGA board that communicates w/ RB)
        self.kcu = get_kcu(self.config.kcu_address, control_hub=True, host=self.config.host, verbose=False)
        if self.kcu == 0:
            raise RuntimeError(f"Failed to establish basic connection to KCU at {self.config.kcu_address}.")

        # Test KCU connection with loopback test
        data = 0xabcd1234
        self.kcu.write_node("LOOPBACK.LOOPBACK", data)
        if data != self.kcu.read_node("LOOPBACK.LOOPBACK"):
            raise RuntimeError(f"KCU loopback communication failed at {self.config.kcu_address}.")

        data_mode = self.config.etroc in ['ETROC1', 'ETROC2']
        
        # Init ReadoutBoard object (from tamalero)
        self.rb = ReadoutBoard(
            self.config.rb_index,
            trigger=True,
            kcu=self.kcu,
            flavor=self.config.flavor,
            config=self.config.configuration,
            data_mode=data_mode,
            etroc=self.config.etroc,
            verbose=False
        )

    # Attempt to close any open connections when deallocated
    def __del__(self):
        pass
    
    # Get any identification data
    def get_id(self) -> str:
        if hasattr(self.rb, 'DAQ_LPGBT'):
            try:
                return f"Tamalero RB #{self.config.rb_index}, Flavor: {self.config.flavor}, ID: {self.rb.DAQ_LPGBT.get_board_id()}"
            except Exception:
                pass
        return f"Tamalero RB #{self.config.rb_index}, Flavor: {self.config.flavor})"
    
    # Shutdown (i.e. disable, not disconnect) the device
    def shutdown(self) -> None:
        pass



    """
    Helper Methods =========================================================
    """
    
    # NOTE: Only defined, never used...? Should this run during init?
    def configure_board(self) -> None:
        
        self.rb.VTRX.get_version()
        
        if not hasattr(self.rb, "TRIG_LPGBT"):
            self.rb.get_trigger()
            
        if self.rb.trigger:
            self.rb.TRIG_LPGBT.power_up_init()
            
        self.rb.configure()
        self.rb.DAQ_LPGBT.invert_links()
        
        if self.rb.trigger:
            self.rb.TRIG_LPGBT.invert_links()
            
        self.rb.enable_etroc_readout()
        self.rb.enable_etroc_readout(slave=True)

    # Read ADCs of all onboard chips
    def read_adcs(self, strict_limits: bool = False) -> dict[str, Any]:
        
        results: dict[str, Any] = {}

        # SCA ADC
        if self.rb.ver < 3 and self.config.flavor == 'small':
            results['SCA'] = self.rb.SCA.read_adcs(check=True, strict_limits=strict_limits)
        
        # DAQ LPGBT ADC
        results['DAQ_LPGBT'] = self.rb.DAQ_LPGBT.read_adcs(check=True, strict_limits=strict_limits)
        
        # Trigger LPGBT ADC
        if self.rb.trigger:
            results['TRIG_LPGBT'] = self.rb.TRIG_LPGBT.read_adcs(check=True, strict_limits=strict_limits)
        
        # MUX ADC
        if hasattr(self.rb, 'MUX64'):
            results['MUX64'] = self.rb.MUX64.read_channels()
            
        # Temperature ADC
        results['temp'] = self.rb.read_temp(verbose=False)

        return results

    # Run built-in eyescan test on LPGBT ADCs
    def run_eyescan(self) -> None:
        self.rb.DAQ_LPGBT.eyescan()

    # Reset and read LPGBT pattern checkers
    def read_pattern_checkers(self, data_src: str = 'prbs') -> dict[str, Any]:
        self.rb.DAQ_LPGBT.set_uplink_group_data_source("normal")
        self.rb.DAQ_LPGBT.set_downlink_data_src(data_src)
        time.sleep(0.1)
        self.rb.DAQ_LPGBT.reset_pattern_checkers()
        time.sleep(0.1)
        return self.rb.DAQ_LPGBT.read_pattern_checkers()

    # Test I2C port of SCA chip
    def test_sca_i2c(self, test_channel: int) -> dict[str, Any]:

        results: dict[str, Any] = {'single_byte': [], 'multi_byte': False}
        
        for n in range(10):
            wr = random.randint(0, 100)
            self.rb.SCA.I2C_write_ctrl(channel=test_channel, data=wr)
            rd = self.rb.SCA.I2C_read_ctrl(channel=test_channel)
            results['single_byte'].append((wr, rd))
            
        write_value = [0x2, 25, (27&240)]
        self.rb.SCA.I2C_write_multi(write_value, channel=test_channel, servant=0x48)
        read_value = self.rb.SCA.I2C_read_multi(channel=test_channel, servant=0x48, nbytes=2, reg=0x2)
        
        if read_value == write_value[1:]:
            results['multi_byte'] = True
            
        return results
