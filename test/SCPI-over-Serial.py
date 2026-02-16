import sys
sys.path.append('../')
sys.path.append('../Cerebellum/')

from Cerebellum.EnvironmentConfig import EnvironmentConfig
from Cerebellum.EnvironmentControl import _PSU
import time

config = EnvironmentConfig()
config.PSUConfigList[0].protocol = "Serial"
config.PSUConfigList[0].COM = "/dev/ttyACM0"
config.PSUConfigList[0].interface = "SCPI"
config.PSUConfigList[0].channel = 0

PSU = _PSU(config.PSUConfigList[0])
PSU.turnOff()
PSU.setVoltage(1.0)
PSU.setCurrent(0.005)
PSU.turnOn()
time.sleep(3)
print(f"Voltage: {PSU.measureVoltage()} V")
print(f"Current: {PSU.measureCurrent()} A")
time.sleep(1)
PSU.turnOff()
