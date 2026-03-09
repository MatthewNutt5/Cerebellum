# Always make sure that Cerebellum and its submodules are on the import path
import sys, os
sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../")
sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../Cerebellum/")

from Cerebellum.EnvironmentConfig import EnvironmentConfig, PSUConfig
from Cerebellum.TestSettings import TestSettings, SetPSUEvent, EvalPSUVoltageEvent, EvalPSUCurrentEvent, EvalPSUPowerEvent
from Cerebellum.EnvironmentControl import runTest

readJSON = False
CAEN = False

config = EnvironmentConfig()
if readJSON:
    config.readJSON("config.json")
else:
    configLV = PSUConfig()
    configLV.displayName = "Low Voltage Power Supply"
    configLV.interface = "SCPI"
    # configLV.protocol = "IP"
    # configLV.IP = "192.168.0.40"
    configLV.protocol = "Serial"
    configLV.COM = "COM7"
    config.PSUConfigList.append(configLV)

    if CAEN:
        configHV = PSUConfig()
        configHV.displayName = "High Voltage Power Supply"
        configHV.interface = "Custom"
        configHV.implementation = "CAENPowerSupply"
        configHV.IP = "192.168.0.1"
        configHV.customConfig = {"systemType" : "SY4527", "linkType" : "TCPIP", "username" : "", "password" : "", "boardSlot" : "0"}
        config.PSUConfigList.append(configHV)

    config.writeJSON("config.json")

settings = TestSettings()
if readJSON:
    settings.readJSON("settings.json")
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
    
    settings.eventList.append(eval_event1)

    if CAEN:
        eval_event2 = EvalPSUCurrentEvent()
        eval_event2.PSUidx = 0
        eval_event2.channel = 0
        settings.eventList.append(eval_event2)

    settings.writeJSON("settings.json")

runTest(config, settings)
