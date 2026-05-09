"""
MainGUI.py
This file contains the main GUI for Cerebellum, consisting of an EnvironmentConfigGUI,
a TestConfigGUI, and a RunTestGUI. These configs are automatically transferred
between tabs. This is the file that should be executed for standard use of Cerebellum.
"""

import sys, os
ABS_DIR = os.path.dirname(os.path.abspath(__file__))

# If running this GUI as a standalone window, add Cerebellum to import path
if __name__ == "__main__":
    sys.path.append(f"{ABS_DIR}/../../") # Cerebellum parent directory

from Cerebellum.GUI.EnvironmentConfigGUI import EnvironmentConfigGUI
from Cerebellum.GUI.TestConfigGUI import TestConfigGUI
from Cerebellum.GUI.RunTestGUI import RunTestGUI

from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget



class MainGUI(QMainWindow):

    def __init__(self):

        super().__init__()
        self.setWindowTitle("Cerebellum GUI")
        self.resize(600, 800)

        # Tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # EnvironmentConfigGUI tab
        self.env_config_tab = EnvironmentConfigGUI()
        self.tabs.addTab(self.env_config_tab, "Environment Config")

        # TestConfigGUI tab
        self.test_config_tab = TestConfigGUI(False)
        self.tabs.addTab(self.test_config_tab, "Test Config")

        # RunTestGUI tab
        self.run_test_tab = RunTestGUI(False)
        self.tabs.addTab(self.run_test_tab, "Run Test")

        # Transfer configs between tabs when tab is changed
        self.tabs.currentChanged.connect(self._tab_changed)


    
    # When the tab is changed, update all tabs with any changes
    def _tab_changed(self) -> None:
        env = self.env_config_tab.get_env()
        self.test_config_tab.set_env(env)
        self.run_test_tab.set_env(env)
        self.run_test_tab.set_test(self.test_config_tab.get_test())



# Run this Python file to test the GUI in a standalone window
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainGUI()
    window.show()
    sys.exit(app.exec())
