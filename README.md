# Cerebellum
Software for configuring and running tests on readout boards for the CMS Endcap Timing Layer at the LHC

Devices: Any device with the module name `Mod` must have two classes inside: `Mod`, representing a controllable instance of the device, and `ModConfig`, reprsenting config data used in the constructor (`__init__`) of `Mod`
