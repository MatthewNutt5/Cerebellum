import sys, os
ABS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(f"{ABS_DIR}/../../") # Cerebellum parent directory
from Cerebellum.EnvironmentConfig import EnvironmentConfig
from Cerebellum.TestConfig import TestConfig
from Cerebellum.Controller import run_test

env_config = EnvironmentConfig()
env_config.read_json(f"{ABS_DIR}/temp_env.json")

test_config = TestConfig()
test_config.read_json(f"{ABS_DIR}/temp_test.json")

run_test(env_config, test_config)
