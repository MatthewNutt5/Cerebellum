"""
_run_test.py

This script is used by RunTestGUI to run a test program as a subprocess.
RunTestGUI writes the current EnvironmentConfig and TestConfig to JSON files
and starts this script in a subprocess. This script will run the test specified
by those JSON files, and RunTestGUI will capture its output for display in the
GUI.

This script can be used to bypass normal GUI operation. Save an
EnvironmentConfig JSON to this directory as "env_config.json", and save a
TestConfig JSON to this directory as "test_config.json". Then, executing this
script in a terminal will use these configurations to immediately run a test,
with the output being displayed in your terminal. Note that these files will be
overwritten and deleted the next time a test is executed through the GUI.
"""

import sys, os
ABS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(f"{ABS_DIR}/../") # Cerebellum parent directory
from Cerebellum.EnvironmentConfig import EnvironmentConfig
from Cerebellum.TestConfig import TestConfig
from Cerebellum.Controller import run_test

env_config = EnvironmentConfig()
env_config.read_json(f"{ABS_DIR}/temp_env.json")

test_config = TestConfig()
test_config.read_json(f"{ABS_DIR}/temp_test.json")

run_test(env_config, test_config)
