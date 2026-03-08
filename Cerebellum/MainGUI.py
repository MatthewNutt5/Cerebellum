import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel

# Ensure the current directory is in the path to import configs
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from EnvironmentConfigGUI import EnvironmentConfigGUI
from TestConfigGUI import TestConfigGUI


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
