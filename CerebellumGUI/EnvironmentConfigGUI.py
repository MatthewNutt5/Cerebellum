# Always make sure that Cerebellum and its submodules are on the import path
import sys, os
ABS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ABS_DIR)                            # CerebellumGUI modules
sys.path.append(f"{ABS_DIR}/../")                   # Cerebellum parent directory
sys.path.append(f"{ABS_DIR}/../Cerebellum/")        # Cerebellum modules
sys.path.append(f"{ABS_DIR}/../Cerebellum/Device/") # Device submodule
from Cerebellum.EnvironmentConfig import EnvironmentConfig
import Cerebellum.Device
from Cerebellum.Device.Device import DeviceConfig

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QPushButton,
                               QScrollArea, QFileDialog, QMessageBox, QGroupBox,
                               QSpinBox, QDoubleSpinBox, QLineEdit, QComboBox, QBoxLayout)
from PySide6.QtCore import Qt

import pkgutil, importlib
import serial.tools.list_ports



class DeviceConfigWidget(QGroupBox):

    def __init__(self, device_config: (DeviceConfig | None) = None, parent=None):

        super().__init__("Device Config", parent)
        self.main_layout = QVBoxLayout(self)

        # Find all modules in Device that can be constructed
        modules: list[str] = []
        for _, full_name, _ in pkgutil.walk_packages(Cerebellum.Device.__path__, Cerebellum.Device.__name__ + "."):
            try:
                module_name = full_name.split(".")[-1]
                module = importlib.import_module(f"Cerebellum.Device.{module_name}")
                constructor = getattr(module, module_name + "Config")
                _ = constructor()
                modules.append(module_name)
            except:
                pass

        # Use these modules/constructors as choices for the Device class
        self.device_class_edit = QComboBox()
        self.device_class_edit.setEditable(False)
        self.device_class_edit.addItems(modules)

        # Ignore wheelEvents so that scrolling will only ever scroll the list of configs
        self.device_class_edit.wheelEvent = (lambda event: event.ignore())

        self.main_layout.addWidget(self.device_class_edit)

        # Init device selection to config class if given, otherwise default to first in modules
        if device_config:
            self.device_class_edit.setCurrentText(device_config.__class__.__name__.replace("Config", ""))
        else:
            self.device_class_edit.setCurrentText(modules[0])

        # Store all field edits in a dict to retrieve field data
        # Store all field widgets (label + edit) in a list that can be cleared
        self.field_edits: dict[str, QWidget] = {}
        self.field_widgets: list[QWidget] = []

        # Add the remove button widget
        # NOTE: Never delete this widget, only add/remove it from the *layout* when updating
        # This way, it remains connected to the parent EnvironmentConfigGUI
        self.remove_button = QPushButton("Remove Device")
        self.remove_button.setStyleSheet("background-color: #ffcccc; color: #cc0000; font-weight: bold;")

        # Update device select to open up fields and allow for data population
        # This populates field_edits with field names and corresponding widgets
        # Also re-run this update any time the device selection changes
        self._update_device_select()
        self.device_class_edit.currentTextChanged.connect(self._update_device_select)

        # Populate with data if provided
        # Type conversions should only be necessary for QComboBox
        if device_config:
            for field_name, field_edit in self.field_edits.items():
                field_value = vars(device_config)[field_name]
                if isinstance(field_edit, QComboBox):
                    field_edit.setCurrentText(str(field_value))
                elif isinstance(field_edit, QSpinBox):
                    field_edit.setValue(int(field_value))
                elif isinstance(field_edit, QDoubleSpinBox):
                    field_edit.setValue(float(field_value))
                elif isinstance(field_edit, QLineEdit):
                    field_edit.setText(str(field_value))

        

    def get_device_config(self):
        
        # First, retrieve a DeviceConfig instance from the current selected device class
        module_name = self.device_class_edit.currentText()
        module = importlib.import_module(f"Cerebellum.Device.{module_name}")
        constructor = getattr(module, module_name + "Config")
        blank_config = constructor()

        # Make a dict for the config based on the current values from edits
        config_dict: dict[str, int | float | str] = {}
        for field_name, field_edit in self.field_edits.items():
            
            # Get the field value according to the edit type
            if isinstance(field_edit, QComboBox):
                field_value = field_edit.currentText()
            elif isinstance(field_edit, (QSpinBox | QDoubleSpinBox)):
                field_value = field_edit.value()
            elif isinstance(field_edit, QLineEdit):
                field_value = field_edit.text()
            
            # Convert the field value according to the type in the blank_config
            field_type = type(getattr(blank_config, field_name))
            if field_type == int:
                config_dict[field_name] = int(field_value)
            elif field_type == float:
                config_dict[field_name] = float(field_value)
            elif field_type == str:
                config_dict[field_name] = str(field_value)
            
        return constructor(vars_dict=config_dict)



    def _update_device_select(self):

        # First, retrieve a DeviceConfig instance from the current selected device class
        module_name = self.device_class_edit.currentText()
        module = importlib.import_module(f"Cerebellum.Device.{module_name}")
        constructor = getattr(module, module_name + "Config")
        blank_config = constructor()

        # Delete the widgets (label + edit) of the current fields
        for field_widget in self.field_widgets:
            self.main_layout.removeWidget(field_widget)
            field_widget.deleteLater()

        # Remove the remove button from the layout
        self.main_layout.removeWidget(self.remove_button)

        # Clear out the dict of edits and the list of widgets
        self.field_edits.clear()
        self.field_widgets.clear()
        
        # Replace them with new fields/widgets corresponding to instance attributes
        for field_name, field_value in vars(blank_config).items():
            # First check if the field has a corresponding _options class attribute
            # If so, construct the field_edit as a ComboBox, and set the options as such
            # Otherwise, construct according to the field's type (e.g. LineEdit, SpinBox, etc.)
            # Also set the current text/value to the default text/value
            if (field_name + "_options") in dir(blank_config.__class__):
                field_edit = QComboBox()
                field_edit.setEditable(False)
                field_edit.addItems([str(item) for item in getattr(blank_config, field_name + "_options")])
                field_edit.setCurrentText(str(field_value))
                field_edit.setMaximumWidth(200)
            elif isinstance(field_value, int):
                field_edit = QSpinBox()
                field_edit.setRange(-2147483648, 2147483647)
                field_edit.setValue(int(field_value))
                field_edit.setMaximumWidth(100)
            elif isinstance(field_value, float):
                field_edit = QDoubleSpinBox()
                field_edit.setRange(float("-inf"), float("inf"))
                field_edit.setValue(float(field_value))
                field_edit.setMaximumWidth(100)
            else:
                field_edit = QLineEdit()
                field_edit.setText(str(field_value))
                field_edit.setMaximumWidth(200)
            
            # Ignore wheelEvents so that scrolling will only ever scroll the list of configs
            field_edit.wheelEvent = (lambda event: event.ignore())
                
            # Special case
            # If a field is called "com", overwrite the widget with a ComboBox that retrieves all COM ports of the computer
            if (field_name == "com"):
                field_edit = QComboBox()
                field_edit.setEditable(True)
                field_edit.addItems([port.name for port in serial.tools.list_ports.comports()])
                field_edit.setCurrentText(str(field_value)) # Might not work?
                field_edit.setMaximumWidth(200)

            # Update the layout with the new field
            # If the field has a corresponding _title class attribute, use that as the label
            # Otherwise, just use the field name
            if (field_name + "_title") in dir(blank_config.__class__):
                self._add_field(getattr(blank_config, field_name + "_title"), field_edit)
            else:
                self._add_field(field_name, field_edit)

            # Update the dict of field edits
            self.field_edits[field_name] = field_edit

        # Add the remove button back to the layout
        self.main_layout.addWidget(self.remove_button)



    def _add_field(self, label_text, edit):
        h_layout = QHBoxLayout()
        label = QLabel(label_text)
        h_layout.addWidget(label)
        h_layout.addWidget(edit)
        self.main_layout.addLayout(h_layout)
        self.field_widgets.append(label)
        self.field_widgets.append(edit)



class EnvironmentConfigGUI(QWidget):

    def __init__(self):
        
        super().__init__()
        self.setWindowTitle("Environment Config Editor")
        self.resize(600, 800)

        self.main_layout = QVBoxLayout(self)

        # Load/Save Buttons
        self.file_buttons_layout = QHBoxLayout()
        self.load_button = QPushButton("Load JSON")
        self.load_button.clicked.connect(self._load_json)
        self.save_button = QPushButton("Save JSON")
        self.save_button.clicked.connect(self._save_json)
        self.file_buttons_layout.addWidget(self.load_button)
        self.file_buttons_layout.addWidget(self.save_button)
        self.main_layout.addLayout(self.file_buttons_layout)

        # DeviceConfig List Area
        self.device_scroll_area = QScrollArea()
        self.device_scroll_area.setWidgetResizable(True)
        self.device_container = QWidget()
        self.device_layout = QVBoxLayout(self.device_container)
        self.device_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.device_scroll_area.setWidget(self.device_container)

        self.main_layout.addWidget(QLabel("Device Configurations:"))
        self.main_layout.addWidget(self.device_scroll_area)

        # Add Device Button
        self.add_device_button = QPushButton("Add Device Config")
        self.add_device_button.clicked.connect(self._add_device_widget)
        self.main_layout.addWidget(self.add_device_button)

        self.device_widgets = []



    def _add_device_widget(self, device_config: (DeviceConfig | None) = None):
        widget = DeviceConfigWidget(device_config)
        self.device_layout.addWidget(widget)
        self.device_widgets.append(widget)
        widget.remove_button.clicked.connect(lambda: self._remove_device_widget(widget))



    def _remove_device_widget(self, widget):
        self.device_layout.removeWidget(widget)
        widget.deleteLater()
        self.device_widgets.remove(widget)



    def _load_json(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Environment Config JSON", "", "JSON Files (*.json)")
        if not filepath:
            return

        try:
            config = EnvironmentConfig()
            config.read_json(filepath)

            # Clear current UI
            for widget in self.device_widgets:
                self._remove_device_widget(widget)

            # Populate UI
            for device in config.device_config_list:
                self._add_device_widget(device)

            QMessageBox.information(self, "Success", f"Successfully loaded configuration from {os.path.basename(filepath)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load JSON file:\n{str(e)}")



    def _save_json(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Environment Config JSON", "", "JSON Files (*.json)")
        if not filepath:
            return

        try:
            config = EnvironmentConfig()

            for widget in self.device_widgets:
                config.device_config_list.append(widget.get_device_config())

            config.write_json(filepath)
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
