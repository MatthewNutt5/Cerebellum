"""
Placeholder
"""

# Prevents TypeError on type hints for Python 3.7 to 3.9
from __future__ import annotations

import sys, os
ABS_DIR = os.path.dirname(os.path.abspath(__file__))

# If running this GUI as a standalone window, add Cerebellum to import path
if __name__ == "__main__":
    sys.path.append(f"{ABS_DIR}/../../") # Cerebellum parent directory

from Cerebellum.GUI.Common import capture_warnings
from Cerebellum.EnvironmentConfig import EnvironmentConfig
from Cerebellum.TestConfig import TestConfig

from PySide6.QtWidgets import  (QApplication, QMainWindow,
                                QWidget, QScrollArea, QGroupBox, QVBoxLayout, QHBoxLayout,
                                QPushButton, QFileDialog, QMessageBox, QLabel,
                                QPlainTextEdit, QLineEdit)
from PySide6.QtCore import QProcess



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



    def set_env(self, config: EnvironmentConfig) -> None:
        self.environment_config = config



    def set_test(self, config: TestConfig) -> None:
        self.test_config = config



    def _log(self, string: str) -> None: self.log_box.appendPlainText(string)



    def _start_test(self) -> None:

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
        self.environment_config.write_json(f"{ABS_DIR}/../temp_env.json")
        self.test_config.write_json(f"{ABS_DIR}/../temp_test.json")
        
        # Clear log box
        self.log_box.clear()

        # Start the test
        self._log("Initiating process.\n")
        self.process = QProcess()
        self.process.finished.connect(self._handle_finish)
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.start(self.environment_config.python_path, [f"{ABS_DIR}/../_run_test.py"])



    def _stop_test(self) -> None:
        if self.process:
            self.process.write(b"STOP\n")

    def _handle_finish(self) -> None:
        self._log("\nProcess has exited.")
        self.process = None
        try:
            os.remove(f"{ABS_DIR}/../temp_env.json")
            os.remove(f"{ABS_DIR}/../temp_test.json")
        except:
            pass

    def _handle_stdout(self) -> None:
        if self.process:
            data = self.process.readAllStandardOutput()
            self._log(str(data.data(), "utf-8").strip())

    def _handle_stderr(self) -> None:
        if self.process:
            data = self.process.readAllStandardError()
            self._log(str(data.data(), "utf-8").strip())

    def _send_input(self) -> None:
        if self.process:
            data = (self.input_line.text() + "\n").encode()
            self.input_line.clear()
            self.process.write(data)


    
    def _load_env_json(self) -> None:
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Environment Config JSON", "", "JSON Files (*.json)")
        if not filepath:
            return

        try:

            with capture_warnings() as warnings:

                config = EnvironmentConfig()
                config.read_json(filepath)
                self.set_env(config)
                
            if warnings:
                string = "Warnings encountered while loading configuration file:"
                for warning in warnings:
                    string += f"\n{warning}"
                QMessageBox.warning(self, "Warning", string)
            else:
                QMessageBox.information(self, "Success", f"Successfully loaded configuration file.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load configuration file:\n{e}")



    def _load_test_json(self) -> None:
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Test Config JSON", "", "JSON Files (*.json)")
        if not filepath:
            return

        try:

            with capture_warnings() as warnings:

                config = TestConfig()
                config.read_json(filepath)
                self.set_test(config)
                
            if warnings:
                string = "Warnings encountered while loading configuration file:"
                for warning in warnings:
                    string += f"\n{warning}"
                QMessageBox.warning(self, "Warning", string)
            else:
                QMessageBox.information(self, "Success", f"Successfully loaded configuration file.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load configuration file:\n{e}")



# Run this Python file to test the GUI in a standalone window
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Run Test")
    window.resize(600, 800)
    central_widget = RunTestGUI(True) # Run in standalone mode
    window.setCentralWidget(central_widget)
    window.show()
    sys.exit(app.exec())
