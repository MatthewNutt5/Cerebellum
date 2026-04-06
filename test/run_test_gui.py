import sys, os
ABS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(f"{ABS_DIR}/../") # Cerebellum parent directory
from Cerebellum.GUI.RunTestGUI import run_test_gui

run_test_gui()
