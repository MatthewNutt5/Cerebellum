# Always make sure that CerebellumGUI and its submodules are on the import path
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/CerebellumGUI/")

from CerebellumGUI.EnvironmentConfigGUI import EnvironmentConfigGUI
from CerebellumGUI.TestConfigGUI import TestConfigGUI

from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel



class MainGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cerebellum Dashboard")
        self.resize(800, 800)

        # Create Tab Widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Tab 1: Environment Config
        self.env_config_tab = EnvironmentConfigGUI()
        self.tabs.addTab(self.env_config_tab, "Environment Config")

        # Tab 2: Test Config
        self.test_config_tab = TestConfigGUI()
        self.tabs.addTab(self.test_config_tab, "Test Config")

        # Tab 3: Placeholder
        self.placeholder_tab = QWidget()
        placeholder_layout = QVBoxLayout(self.placeholder_tab)
        placeholder_label = QLabel("Placeholder Tab")
        placeholder_layout.addWidget(placeholder_label)
        self.tabs.addTab(self.placeholder_tab, "Placeholder")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainGUI()
    window.show()
    sys.exit(app.exec())
