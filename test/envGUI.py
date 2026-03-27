import sys, os
ABS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(f"{ABS_DIR}/../") # Cerebellum parent directory
from Cerebellum.GUI.EnvironmentConfigGUI import envGUI

envGUI()
