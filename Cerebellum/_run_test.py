"""
_run_test.py

This script is primarily used by RunTestGUI to ...

This script can be used to bypass normal GUI operation. Save an
EnvironmentConfig JSON to this directory as "env_config.json", and save a
TestConfig JSON to this directory as "test_config.json". Then, executing this
script in a terminal will use these configurations to immediately run a test,
with the output being displayed in your terminal.
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
