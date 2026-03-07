import sys
sys.path.append('../')
sys.path.append('../Cerebellum/')

from Cerebellum.EnvironmentConfig import EnvironmentConfig, PSUConfig
from Cerebellum.TestSettings import TestSettings, SetPSUEvent, EvalPSUVoltageEvent, EvalPSUCurrentEvent
from Cerebellum.EnvironmentControl import runTest

readJSON = False

config = EnvironmentConfig()
if readJSON:
    config.readJSON("config.json")
else:
    psu_config = PSUConfig()
    psu_config.displayName = "Low Voltage Power Supply"
    psu_config.interface = "SCPI"
    # psu_config.protocol = "IP"
    # psu_config.IP = "192.168.0.40"
    psu_config.protocol = "Serial"
    psu_config.COM = "COM7"
    config.PSUConfigList.append(psu_config)

    config.writeJSON("config.json")

settings = TestSettings()
if readJSON:
    settings.readJSON("settings.json")
else:
    set_event = SetPSUEvent()
    set_event.PSUidx = 0
    set_event.channel = 0
    set_event.voltage = 9.0
    set_event.current = 6.0
    settings.PSUSettingsList.append(set_event)

    eval_event = EvalPSUCurrentEvent()
    eval_event.PSUidx = 0
    eval_event.channel = 0
    settings.eventList.append(eval_event)

    settings.writeJSON("settings.json")

#runTest(config, settings)
