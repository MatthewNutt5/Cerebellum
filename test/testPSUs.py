import sys
sys.path.append('../')
sys.path.append('../Cerebellum/')

from Cerebellum.EnvironmentConfig import EnvironmentConfig, PSUConfig
from Cerebellum.TestSettings import TestSettings, PSUSettings, Criterion
from Cerebellum.EnvironmentControl import runTest

readJSON = False

config = EnvironmentConfig()
if readJSON:
    config.readJSON("config.json")
else:
    config.PSUConfigList.append(PSUConfig())
    config.PSUConfigList[0].protocol = "IP"
    config.PSUConfigList[0].IP = "192.168.0.40"
    config.PSUConfigList[0].interface = "SCPI"
    config.PSUConfigList[0].channel = 0
    config.writeJSON("config.json")

settings = TestSettings()
if readJSON:
    settings.readJSON("settings.json")
else:
    settings.PSUSettingsList.append(PSUSettings())
    settings.PSUSettingsList[0].voltage = 1.0
    settings.PSUSettingsList[0].current = 0.015
    settings.criteriaList.append(Criterion("PSUCurrent"))
    settings.criteriaList[0].PSUidx = 0
    settings.criteriaList[0].ineq = "<"
    settings.criteriaList[0].PSUCurrent = 0.1
    settings.writeJSON("settings.json")

runTest(config, settings)
