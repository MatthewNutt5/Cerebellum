"""
TestConfig.py
This file contains the TestConfig class, which is used to specify the conditions
of a test - power supply voltages/currents, Tamalero programs, etc.
Configurations can be stored in JSON files for later use. Primarily used by
runTest.py.

This file also contains the CriterionConfig class, which is a helper class used
to specify an individual criterion the test should evaluate.
TODO: add json support
TODO: types of criterion: current, voltage, DAQ transient, Tamalero script
"""

from json import dump, load



class TestConfig:

    def __init__(self):

        self.LVPSVoltage    = 0.0       # If CV, set voltage to this; if CC, this is voltage limit
        self.LVPSCurrent    = 0.0       # If CV, this is current limit; if CC, set current to this
        self.LVPSConstCurr  = False     # Will the LVPS run in CC mode? (False = CV)
        self.HVPSVoltage    = 0.0       # "
        self.HVPSCurrent    = 0.0       # "
        self.HVPSConstCurr  = False     # "
        self.AuxPSUSettings = []        # Ditto the above, as ordered triples [V, C, T/F]
        self.criteria       = []        # List of CriterionConfig objects



class CriterionConfig:

    def __init__(self, type):

        self.type = type

        if type == "PSUCurrent":
            self.PSUCurrent