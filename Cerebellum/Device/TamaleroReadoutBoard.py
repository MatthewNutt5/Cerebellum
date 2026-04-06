from typing import Any
from Cerebellum.Device import Device, DeviceConfig
from tamalero.ReadoutBoard import ReadoutBoard
from tamalero.utils import get_kcu

class TamaleroReadoutBoardConfig(DeviceConfig):
    
    kcu_address_title: str = "KCU IP Address"
    host_title: str = "Control Hub Host"
    rb_index_title: str = "Readout Board Index"
    flavor_title: str = "Board Flavor"
    flavor_options: list[str] = ['small', 'medium', 'large']
    configuration_title: str = "Configuration"
    configuration_options: list[str] = ['default', 'emulator', 'modulev0', 'modulev0b', 'multimodule', 'mux64', 'modulev1', 'modulev2']
    etroc_title: str = "ETROC Version"
    etroc_options: list[str] = ['ETROC1', 'ETROC2']

    def __init__(self, vars_dict: dict[str, Any] = {}):
        if vars_dict:
            vars(self).update(vars_dict)
        else:
            self.display_name: str = "Tamalero Readout Board"
            self.kcu_address: str = "192.168.0.10"
            self.host: str = "localhost"
            self.rb_index: int = 0
            self.flavor: str = "small"
            self.configuration: str = "default"
            self.etroc: str = "ETROC2"


class TamaleroReadoutBoard(Device):
    
    def __init__(self, config: TamaleroReadoutBoardConfig):
        self.config = config
        self.kcu = None
        self.rb = None

        self.kcu = get_kcu(self.config.kcu_address, control_hub=True, host=self.config.host, verbose=False)
        if self.kcu == 0:
            raise RuntimeError(f"Failed to establish basic connection to KCU at {self.config.kcu_address}.")

        data = 0xabcd1234
        self.kcu.write_node("LOOPBACK.LOOPBACK", data)
        if data != self.kcu.read_node("LOOPBACK.LOOPBACK"):
            raise RuntimeError("KCU loopback communication failed.")

        data_mode = self.config.etroc in ['ETROC1', 'ETROC2']
        
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

    def __del__(self):
        self.rb = None
        self.kcu = None

    def get_id(self) -> str:
        if self.rb and hasattr(self.rb, "DAQ_LPGBT"):
            try:
                res = self.rb.DAQ_LPGBT.get_board_id()
                return f"Tamalero RB {self.config.rb_index} ID: {res}"
            except Exception:
                pass
        return f"Tamalero RB {self.config.rb_index} (Flavor: {self.config.flavor})"
        
    def configure_board(self):
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

    #test methods???
    def read_adcs(self, strict_limits: bool = False) -> dict:
        results = {}
        
        if self.rb.ver < 3 and self.config.flavor == 'small':
            results['SCA'] = self.rb.SCA.read_adcs(check=True, strict_limits=strict_limits)
            
        results['DAQ_LPGBT'] = self.rb.DAQ_LPGBT.read_adcs(check=True, strict_limits=strict_limits)
        
        if self.rb.trigger:
            results['TRIG_LPGBT'] = self.rb.TRIG_LPGBT.read_adcs(check=True, strict_limits=strict_limits)
            
        if hasattr(self.rb, "MUX64"):
            results['MUX64'] = self.rb.MUX64.read_channels()
            
        results['temp'] = self.rb.read_temp(verbose=False)
        return results

    def run_eyescan(self):
        self.rb.DAQ_LPGBT.eyescan()

    def reset_pattern_checker(self, data_src: str = 'prbs'):
        import time
        self.rb.DAQ_LPGBT.set_uplink_group_data_source("normal")
        self.rb.DAQ_LPGBT.set_downlink_data_src(data_src)
        time.sleep(0.1)
        self.rb.DAQ_LPGBT.reset_pattern_checkers()
        time.sleep(0.1)

    def read_pattern_checker(self):
        import time
        time.sleep(1)
        self.rb.DAQ_LPGBT.read_pattern_checkers()

    def test_sca_i2c(self, test_channel: int = 3):
        import random
        results = {'single_byte': [], 'multi_byte': False}
        
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