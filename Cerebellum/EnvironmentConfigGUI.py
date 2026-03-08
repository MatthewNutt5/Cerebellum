import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QScrollArea, QFileDialog, QMessageBox, QGroupBox, QSpinBox, QComboBox)
from PySide6.QtCore import Qt

# Ensure the current directory is in the path to import EnvironmentConfig
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from EnvironmentConfig import EnvironmentConfig, PSUConfig

class PSUConfigWidget(QGroupBox):
    def __init__(self, psu_config=None, parent=None):
        super().__init__("PSU Config", parent)
        self.layout = QVBoxLayout(self)

        # Fields
        self.displayname_edit = QLineEdit()

        self.protocol_edit = QComboBox()
        self.protocol_edit.setEditable(False)
        self.protocol_edit.addItems(["IP", "Serial"])

        self.ip_edit = QLineEdit()
        self.com_edit = QLineEdit()
        self.baudrate_spin = QSpinBox()
        self.baudrate_spin.setRange(0, 10000000)
        self.interface_edit = QComboBox()
        self.interface_edit.setEditable(False)
        self.interface_edit.addItems(["SCPI", "Custom"])

        # Custom Implementation Fields
        self.implementation_edit = QLineEdit()
        self.implementation_edit.setReadOnly(True)
        self.implementation_button = QPushButton("Upload File")
        self.implementation_button.clicked.connect(self.upload_implementation)

        # Populate with data if provided
        if psu_config:
            self.displayname_edit.setText(str(psu_config.displayName))
            self.protocol_edit.setCurrentText(str(psu_config.protocol))
            self.ip_edit.setText(str(psu_config.IP))
            self.com_edit.setText(str(psu_config.COM))
            self.baudrate_spin.setValue(int(psu_config.baudrate))
            self.interface_edit.setCurrentText(str(psu_config.interface))
            self.implementation_edit.setText(str(getattr(psu_config, 'implementation', '')))
        else:
            self.baudrate_spin.setValue(115200)

        # Layout setup
        self.add_field("Display Name:", self.displayname_edit)
        self.add_field("Protocol:", self.protocol_edit)
        self.add_field("IP Address:", self.ip_edit)
        self.add_field("COM Port:", self.com_edit)
        self.add_field("Baudrate:", self.baudrate_spin)
        self.add_field("Interface:", self.interface_edit)

        # Implementation layout
        self.implementation_layout = QHBoxLayout()
        self.implementation_label = QLabel("Implementation:")
        self.implementation_layout.addWidget(self.implementation_label)
        self.implementation_layout.addWidget(self.implementation_edit)
        self.implementation_layout.addWidget(self.implementation_button)
        self.layout.addLayout(self.implementation_layout)

        # Remove button
        self.remove_button = QPushButton("Remove PSU")
        self.remove_button.setStyleSheet("background-color: #ffcccc; color: #cc0000; font-weight: bold;")
        self.layout.addWidget(self.remove_button)

        # Initial visibility and connection
        self.update_implementation_visibility()
        self.interface_edit.currentTextChanged.connect(self.update_implementation_visibility)

    def upload_implementation(self):
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Implementation File", repo_root, "Python Files (*.py)")
        if filepath:
            try:
                rel_path = os.path.relpath(filepath, repo_root)
                self.implementation_edit.setText(rel_path)
            except ValueError:
                self.implementation_edit.setText(filepath)

    def update_implementation_visibility(self):
        is_custom = self.interface_edit.currentText() == "Custom"
        self.implementation_label.setVisible(is_custom)
        self.implementation_edit.setVisible(is_custom)
        self.implementation_button.setVisible(is_custom)

    def add_field(self, label_text, widget):
        h_layout = QHBoxLayout()
        label = QLabel(label_text)
        h_layout.addWidget(label)
        h_layout.addWidget(widget)
        self.layout.addLayout(h_layout)

    def get_psu_config(self):
        config = PSUConfig()
        config.displayName = self.displayname_edit.text()
        config.protocol = self.protocol_edit.currentText()
        config.IP = self.ip_edit.text()
        config.COM = self.com_edit.text()
        config.baudrate = self.baudrate_spin.value()
        config.interface = self.interface_edit.currentText()
        config.implementation = self.implementation_edit.text()
        return config


class EnvironmentConfigGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Environment Config Editor")
        self.resize(600, 800)

        self.main_layout = QVBoxLayout(self)

        # Load/Save Buttons
        self.file_buttons_layout = QHBoxLayout()
        self.load_button = QPushButton("Load JSON")
        self.load_button.clicked.connect(self.load_json)
        self.save_button = QPushButton("Save JSON")
        self.save_button.clicked.connect(self.save_json)
        self.file_buttons_layout.addWidget(self.load_button)
        self.file_buttons_layout.addWidget(self.save_button)
        self.main_layout.addLayout(self.file_buttons_layout)

        # EnvironmentConfig Fields
        self.env_group = QGroupBox("Environment Config")
        self.env_layout = QVBoxLayout(self.env_group)

        self.addressRB_layout = QHBoxLayout()
        self.addressRB_label = QLabel("addressRB:")
        self.addressRB_edit = QLineEdit()
        self.addressRB_layout.addWidget(self.addressRB_label)
        self.addressRB_layout.addWidget(self.addressRB_edit)
        self.env_layout.addLayout(self.addressRB_layout)

        self.main_layout.addWidget(self.env_group)

        # PSUConfig List Area
        self.psu_scroll_area = QScrollArea()
        self.psu_scroll_area.setWidgetResizable(True)
        self.psu_container = QWidget()
        self.psu_layout = QVBoxLayout(self.psu_container)
        self.psu_layout.setAlignment(Qt.AlignTop)
        self.psu_scroll_area.setWidget(self.psu_container)

        self.main_layout.addWidget(QLabel("PSU Configurations:"))
        self.main_layout.addWidget(self.psu_scroll_area)

        # Add PSU Button
        self.add_psu_button = QPushButton("Add PSU Config")
        self.add_psu_button.clicked.connect(self.add_psu_widget)
        self.main_layout.addWidget(self.add_psu_button)

        self.psu_widgets = []

    def add_psu_widget(self, psu_config=None):
        widget = PSUConfigWidget(psu_config)
        self.psu_layout.addWidget(widget)
        self.psu_widgets.append(widget)
        widget.remove_button.clicked.connect(lambda: self.remove_psu_widget(widget))

    def remove_psu_widget(self, widget):
        self.psu_layout.removeWidget(widget)
        widget.deleteLater()
        if widget in self.psu_widgets:
            self.psu_widgets.remove(widget)

    def load_json(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Environment Config JSON", "", "JSON Files (*.json)")
        if not filepath:
            return

        try:
            config = EnvironmentConfig()
            config.readJSON(filepath)

            # Clear current UI
            self.addressRB_edit.clear()
            for widget in list(self.psu_widgets):
                self.remove_psu_widget(widget)

            # Populate UI
            self.addressRB_edit.setText(str(config.addressRB))
            for psu in config.PSUConfigList:
                self.add_psu_widget(psu)

            QMessageBox.information(self, "Success", f"Successfully loaded configuration from {os.path.basename(filepath)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load JSON file:\n{str(e)}")

    def save_json(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Environment Config JSON", "", "JSON Files (*.json)")
        if not filepath:
            return

        try:
            config = EnvironmentConfig()
            config.addressRB = self.addressRB_edit.text()

            for widget in self.psu_widgets:
                config.PSUConfigList.append(widget.get_psu_config())

            config.writeJSON(filepath)
            QMessageBox.information(self, "Success", f"Successfully saved configuration to {os.path.basename(filepath)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save JSON file:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Environment Config Editor")
    window.resize(600, 800)
    central_widget = EnvironmentConfigGUI()
    window.setCentralWidget(central_widget)
    window.show()
    sys.exit(app.exec())
