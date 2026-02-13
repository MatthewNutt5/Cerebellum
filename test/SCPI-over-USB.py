import sys
sys.path.append('../Cerebellum/')

from Cerebellum.EnvironmentConfig import EnvironmentConfig
from Cerebellum.EnvironmentControl import _PSU

config = EnvironmentConfig()
config.PSUConfigList[0].connector = "USB"
config.PSUConfigList[0].interface = "SCPI"

PSU = _PSU(config.PSUConfigList[0])
PSU.turnOff()
PSU.setVoltage(1.0)
PSU.setCurrent(0.005)
PSU.turnOn()
print(PSU.measureVoltage())
print(PSU.measureCurrent())
PSU.turnOff()
