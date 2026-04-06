"""
Placeholder
"""

from Cerebellum.GUI.Common import capture_warnings, logging_to_box
from Cerebellum.EnvironmentConfig import EnvironmentConfig
from Cerebellum.TestConfig import TestConfig
from Cerebellum.Controller import run_test

from PySide6.QtWidgets import  (QApplication, QMainWindow,
                                QWidget, QScrollArea, QGroupBox, QVBoxLayout, QHBoxLayout,
                                QPushButton, QFileDialog, QMessageBox, QLabel,
                                QPlainTextEdit)

import sys



class RunTestGUI(QWidget):

    def __init__(self, standalone: bool):

        super().__init__()
        self.main_layout = QVBoxLayout(self)

        # Environment and Test configs
        self.environment_config: (EnvironmentConfig | None) = None
        self.test_config: (TestConfig | None) = None

        # Load Config buttons
        # Connect to load methods
        if standalone:
            self.file_buttons_layout = QHBoxLayout()
            self.load_env_button = QPushButton("Load EnvironmentConfig JSON")
            self.load_env_button.clicked.connect(self._load_env_json)
            self.load_test_button = QPushButton("Load TestConfig JSON")
            self.load_test_button.clicked.connect(self._load_test_json)
            self.file_buttons_layout.addWidget(self.load_env_button)
            self.file_buttons_layout.addWidget(self.load_test_button)
            self.main_layout.addLayout(self.file_buttons_layout)

        # Run test button
        self.run_button_layout = QHBoxLayout()
        self.run_test_button = QPushButton("Run Test")
        self.run_test_button.clicked.connect(self._run_test)
        self.run_button_layout.addWidget(self.run_test_button)
        self.main_layout.addLayout(self.run_button_layout)

        # Log box
        self.log_box_layout = QVBoxLayout()
        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box_layout.addWidget(self.log_box)
        self.main_layout.addLayout(self.log_box_layout)



    def _run_test(self):

        # Check for configs
        if not self.environment_config:
            QMessageBox.critical(self, "Error", "An environment config must be loaded to run a test.")
            return
        if not self.test_config:
            QMessageBox.critical(self, "Error", "A test config must be loaded to run a test.")
            return
        
        # Clear log box
        self.log_box.clear()

        # Run the test
        with logging_to_box(self.log_box):
            run_test(self.environment_config, self.test_config)



    def _load_env_json(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Environment Config JSON", "", "JSON Files (*.json)")
        if not filepath:
            return

        try:

            with capture_warnings() as warnings:

                self.environment_config = EnvironmentConfig()
                self.environment_config.read_json(filepath)
                
            if warnings:
                string = "Warnings encountered while loading configuration file:"
                for warning in warnings:
                    string += f"\n{warning}"
                QMessageBox.warning(self, "Warning", string)
            else:
                QMessageBox.information(self, "Success", f"Successfully loaded configuration file.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load configuration file:\n{e}")



    def _load_test_json(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Test Config JSON", "", "JSON Files (*.json)")
        if not filepath:
            return

        try:

            with capture_warnings() as warnings:

                self.test_config = TestConfig()
                self.test_config.read_json(filepath)
                
            if warnings:
                string = "Warnings encountered while loading configuration file:"
                for warning in warnings:
                    string += f"\n{warning}"
                QMessageBox.warning(self, "Warning", string)
            else:
                QMessageBox.information(self, "Success", f"Successfully loaded configuration file.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load configuration file:\n{e}")



# Run the GUI as a standalone window
def run_test_gui() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Run Test")
    window.resize(600, 800)
    central_widget = RunTestGUI(True) # Run in standalone mode
    window.setCentralWidget(central_widget)
    window.show()
    sys.exit(app.exec())
