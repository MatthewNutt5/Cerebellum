"""
Placeholder
"""

from Cerebellum.GUI.EnvironmentConfigGUI import EnvironmentConfigGUI
from Cerebellum.GUI.TestConfigGUI import TestConfigGUI
from Cerebellum.GUI.RunTestGUI import RunTestGUI

from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget

import sys



class MainGUI(QMainWindow):

    def __init__(self):

        super().__init__()
        self.setWindowTitle("Cerebellum GUI")
        self.resize(600, 800)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self._tab_changed)
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


    
    def _tab_changed(self, index: int) -> None:
        
        if (index == 1): # Changed to TestConfig
            self.test_config_tab.set_env(self.env_config_tab.get_env())
        elif (index == 2): # Changed to RunTest
            self.run_test_tab.set_env(self.env_config_tab.get_env())
            self.run_test_tab.set_test(self.test_config_tab.get_test())



# Run the GUI as a standalone window
def main_gui() -> None:
    app = QApplication(sys.argv)
    window = MainGUI()
    window.show()
    sys.exit(app.exec())
