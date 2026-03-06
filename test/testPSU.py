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
    config.PSUConfigList.append(PSUConfig())
    config.PSUConfigList[0].displayName = "Low Voltage Power Supply"
    config.PSUConfigList[0].interface = "SCPI"
    # config.PSUConfigList[0].protocol = "IP"
    # config.PSUConfigList[0].IP = "192.168.0.40"
    config.PSUConfigList[0].protocol = "Serial"
    config.PSUConfigList[0].COM = "COM7"
    config.writeJSON("config.json")

settings = TestSettings()
if readJSON:
    settings.readJSON("settings.json")
else:
    settings.PSUSettingsList.append(SetPSUEvent())
    settings.PSUSettingsList[0].PSUidx = 0
    settings.PSUSettingsList[0].channel = 0
    settings.PSUSettingsList[0].voltage = 9.0
    settings.PSUSettingsList[0].current = 6.0
    settings.eventList.append(EvalPSUCurrentEvent())
    settings.eventList[0].PSUidx = 0
    settings.eventList[0].channel = 0
    settings.writeJSON("settings.json")

runTest(config, settings)
