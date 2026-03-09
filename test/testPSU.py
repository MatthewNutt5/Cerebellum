import sys
sys.path.append('../')
sys.path.append('../Cerebellum/')

from Cerebellum.EnvironmentConfig import EnvironmentConfig, PSUConfig
from Cerebellum.TestSettings import TestSettings, SetPSUEvent, EvalPSUVoltageEvent, EvalPSUCurrentEvent
from Cerebellum.EnvironmentControl import runTest

readJSON = False
CAEN = True

config = EnvironmentConfig()
if readJSON:
    config.readJSON("config.json")
else:
    configLV = PSUConfig()
    configLV.displayName = "Low Voltage Power Supply"
    configLV.interface = "SCPI"
    configLV.protocol = "IP"
    configLV.IP = "192.168.0.40"
    # configLV.protocol = "Serial"
    # configLV.COM = "COM7"
    config.PSUConfigList.append(configLV)

    if CAEN:
        configHV = PSUConfig()
        configHV.displayName = "High Voltage Power Supply"
        configHV.interface = "Custom"
        configHV.IP = "192.168.0.40"
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
    setEvent1.voltage = 1.0
    setEvent1.current = 0.1
    settings.PSUSettingsList.append(setEvent1)

    if CAEN:
        setEvent2 = SetPSUEvent()
        setEvent2.PSUidx = 1 # The HV was the second PSU added, so it's at index 1
        setEvent2.channel = 0
        setEvent2.voltage = 2.0
        setEvent2.current = 0.5
        settings.PSUSettingsList.append(setEvent2)

    eval_event = EvalPSUCurrentEvent()
    eval_event.PSUidx = 0
    eval_event.channel = 0
    settings.eventList.append(eval_event)

    if CAEN:
        eval_event = EvalPSUCurrentEvent()
        eval_event.PSUidx = 0
        eval_event.channel = 0
        settings.eventList.append(eval_event)

    settings.writeJSON("settings.json")

runTest(config, settings)
