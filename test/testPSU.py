# Always make sure that Cerebellum and its submodules are on the import path
import sys, os
sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../")
sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../Cerebellum/")

from Cerebellum.EnvironmentConfig import EnvironmentConfig, PSUConfig
from Cerebellum.TestConfig import TestConfig, SetPSUEvent, EvalPSUVoltageEvent, EvalPSUCurrentEvent, EvalPSUPowerEvent
from Cerebellum.Controller import run_test

read_json = False
CAEN = False

config = EnvironmentConfig()
if read_json:
    config.read_json("config.json")
else:
    configLV = PSUConfig()
    configLV.display_name = "Low Voltage Power Supply"
    configLV.interface = "SCPI"
    # configLV.protocol = "IP"
    # configLV.ip = "192.168.0.40"
    configLV.protocol = "Serial"
    configLV.com = "COM7"
    config.PSUConfigList.append(configLV)

    if CAEN:
        configHV = PSUConfig()
        configHV.display_name = "High Voltage Power Supply"
        configHV.interface = "Custom"
        configHV.implementation = "CAENPowerSupply"
        configHV.ip = "192.168.0.1"
        configHV.customConfig = {"systemType" : "SY4527", "linkType" : "TCPIP", "username" : "", "password" : "", "boardSlot" : "0"}
        config.PSUConfigList.append(configHV)

    config.write_json("config.json")

settings = TestConfig()
if read_json:
    settings.read_json("settings.json")
else:
    setEvent1 = SetPSUEvent()
    setEvent1.PSUidx = 0 # The LV was the first PSU added, so it's at index 0
    setEvent1.channel = 0
    setEvent1.voltage = 9.0
    setEvent1.current = 6.0
    settings.PSUSettingsList.append(setEvent1)

    if CAEN:
        setEvent2 = SetPSUEvent()
        setEvent2.PSUidx = 1 # The HV was the second PSU added, so it's at index 1
        setEvent2.channel = 0
        setEvent2.voltage = 2.0
        setEvent2.current = 0.5
        settings.PSUSettingsList.append(setEvent2)

    eval_event1 = EvalPSUPowerEvent()
    eval_event1.PSUidx = 0
    eval_event1.channel = 0
    eval_event1.PowerLow = 3.5
    eval_event1.PowerHigh = 4.0
    
    settings.event_list.append(eval_event1)

    if CAEN:
        eval_event2 = EvalPSUCurrentEvent()
        eval_event2.PSUidx = 0
        eval_event2.channel = 0
        settings.event_list.append(eval_event2)

    settings.write_json("settings.json")

run_test(config, settings)
