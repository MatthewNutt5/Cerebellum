# Always make sure that Cerebellum and its submodules are on the import path
import sys, os
ABS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(f"{ABS_DIR}/../")                   # Cerebellum parent directory
sys.path.append(f"{ABS_DIR}/../Cerebellum/")        # Cerebellum modules
sys.path.append(f"{ABS_DIR}/../Cerebellum/Device/") # Device submodule
from Cerebellum.EnvironmentConfig import EnvironmentConfig
from Cerebellum.TestConfig import TestConfig
from Cerebellum.Event import *
from Cerebellum.Controller import run_test
from Cerebellum.Device.SCPIPowerSupply import SCPIPowerSupplyConfig
#from Cerebellum.Device.CAENPowerSupply import CAENPowerSupplyConfig


read_json = False
CAEN = False



env_config = EnvironmentConfig()

if read_json:
    env_config.read_json("env_config.json")
else:
    config_lv = SCPIPowerSupplyConfig()
    config_lv.display_name = "Low Voltage Power Supply"
    config_lv.protocol = "IP"
    config_lv.ip = "192.168.0.40"
    config_lv.com = "COM7"
    env_config.device_config_list.append(config_lv)

    if CAEN:
        config_hv = CAENPowerSupplyConfig()
        config_hv.display_name = "High Voltage Power Supply"
        config_hv.ip = "192.168.0.1"
        config_hv.username = ""
        config_hv.password = ""
        config_hv.board_slot = 0
        env_config.device_config_list.append(config_hv)

    env_config.write_json("env_config.json")



test_config = TestConfig()

if read_json:
    test_config.read_json("test_config.json")
else:
    test_config.event_list.append(WaitEvent())

    event = SetPSUEvent()
    event.comment = "Power the RB"
    event.device_idx = 0 # The LV was the first PSU added, so it's at index 0
    event.channel = 0
    event.voltage = 9.0
    event.current = 6.0
    test_config.event_list.append(event)

    event = SleepEvent()
    event.comment = "Wait for 3 seconds"
    test_config.event_list.append(event)

    if CAEN:
        event = SetPSUEvent()
        event.device_idx = 1 # The HV was the second PSU added, so it's at index 1
        event.channel = 0
        event.voltage = 2.0
        event.current = 0.5
        test_config.event_list.append(event)

    event = EvalPSUPowerEvent()
    event.device_idx = 0
    event.channel = 0
    event.power_low = 3.5
    event.power_high = 4.0
    test_config.event_list.append(event)

    if CAEN:
        event = EvalPSUCurrentEvent()
        event.device_idx = 0
        event.channel = 0
        test_config.event_list.append(event)

    test_config.write_json("test_config.json")

run_test(env_config, test_config)
