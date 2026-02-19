import sys
sys.path.append('../')
sys.path.append('../Cerebellum/')

from Cerebellum.EnvironmentConfig import EnvironmentConfig, PSUConfig
from Cerebellum.TestSettings import TestSettings, PSUSettings, Criterion
from Cerebellum.EnvironmentControl import runTest

config = EnvironmentConfig()
config.PSUConfigList.append(PSUConfig())
config.PSUConfigList[0].protocol = "IP"
config.PSUConfigList[0].IP = "192.168.0.40"
config.PSUConfigList[0].interface = "SCPI"
config.PSUConfigList[0].channel = 0

settings = TestSettings()
settings.PSUSettingsList.append(PSUSettings())
settings.PSUSettingsList[0].voltage = 1.0
settings.PSUSettingsList[0].current = 0.005
settings.criteriaList.append(Criterion("PSUCurrent"))
settings.criteriaList[0].PSUidx = 0
settings.criteriaList[0].ineq = "<"
settings.criteriaList[0].PSUCurrent = 0.1

runTest(config, settings)
