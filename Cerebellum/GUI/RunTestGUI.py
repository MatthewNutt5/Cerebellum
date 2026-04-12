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
                                QPlainTextEdit, QLineEdit)
from PySide6.QtCore import QProcess

import sys, os
ABS_DIR = os.path.dirname(os.path.abspath(__file__))



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

        # Process for running a test
        # Kept as an instance variable so it doesn't get garbage collected
        # when _start_test completes
        self.process: (QProcess | None) = None

        # Start/stop test button
        self.control_buttons_layout = QHBoxLayout()
        self.start_test_button = QPushButton("Start Test")
        self.start_test_button.clicked.connect(self._start_test)
        self.stop_test_button = QPushButton("Stop Test")
        self.stop_test_button.clicked.connect(self._stop_test)
        self.control_buttons_layout.addWidget(self.start_test_button)
        self.control_buttons_layout.addWidget(self.stop_test_button)
        self.main_layout.addLayout(self.control_buttons_layout)

        # Log box
        self.log_box_layout = QVBoxLayout()
        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box_layout.addWidget(self.log_box)
        
        # Input field
        self.input_line = QLineEdit()
        self.input_line.returnPressed.connect(self._send_input)
        self.log_box_layout.addWidget(self.input_line)

        self.main_layout.addLayout(self.log_box_layout)



    def _log(self, string: str): self.log_box.appendPlainText(string)



    def _start_test(self):

        # Check for configs
        if not self.environment_config:
            QMessageBox.critical(self, "Error", "An environment config must be loaded to run a test.")
            return
        if not self.test_config:
            QMessageBox.critical(self, "Error", "A test config must be loaded to run a test.")
            return
        if self.process:
            QMessageBox.critical(self, "Error", "A test process is already running. End the process to start another test.")
            return
        
        # Write configs to temp JSONs
        self.environment_config.write_json(f"{ABS_DIR}/temp_env.json")
        self.test_config.write_json(f"{ABS_DIR}/temp_test.json")
        
        # Clear log box
        self.log_box.clear()

        # Start the test
        self._log("Initiating process.")
        self.process = QProcess()
        self.process.finished.connect(self._handle_finish)
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.start("python", [f"{ABS_DIR}/run_cerebellum_test.py"])



    def _stop_test(self):
        if self.process:
            self.process.write(b"STOP\n")

    def _handle_finish(self):
        self._log("Process has exited.")
        self.process = None
        try:
            os.remove(f"{ABS_DIR}/temp_env.json")
            os.remove(f"{ABS_DIR}/temp_test.json")
        except:
            pass

    def _handle_stdout(self):
        if self.process:
            data = self.process.readAllStandardOutput()
            self._log(str(data.data(), "utf-8").strip())

    def _handle_stderr(self):
        if self.process:
            data = self.process.readAllStandardError()
            self._log(str(data.data(), "utf-8").strip())

    def _send_input(self):
        if self.process:
            data = (self.input_line.text() + "\n").encode()
            self.input_line.clear()
            self.process.write(data)



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
