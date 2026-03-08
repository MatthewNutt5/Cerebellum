import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QScrollArea, QFileDialog, QMessageBox, QGroupBox, QSpinBox, QComboBox, QDoubleSpinBox, QFrame)
from PySide6.QtCore import Qt

# Ensure the current directory is in the path to import configs
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from EnvironmentConfig import EnvironmentConfig
from TestSettings import TestSettings, Event, SetPSUEvent, EvalPSUVoltageEvent, EvalPSUCurrentEvent, EvalPSUPowerEvent


class SetPSUEventWidget(QGroupBox):
    def __init__(self, psu_config_list, event=None, parent=None):
        super().__init__("Set PSU Event", parent)
        self.layout = QVBoxLayout(self)
        self.psu_config_list = psu_config_list

        self.psu_idx_combo = QComboBox()
        self.update_psu_dropdown()

        self.channel_spin = QSpinBox()
        self.channel_spin.setRange(0, 1000)

        self.enable_combo = QComboBox()
        self.enable_combo.addItems(["True", "False"])

        self.voltage_spin = QDoubleSpinBox()
        self.voltage_spin.setRange(0.0, 10000.0)
        self.voltage_spin.setDecimals(3)

        self.current_spin = QDoubleSpinBox()
        self.current_spin.setRange(0.0, 10000.0)
        self.current_spin.setDecimals(3)

        if event and isinstance(event, SetPSUEvent):
            self.psu_idx_combo.setCurrentIndex(event.PSUidx)
            self.channel_spin.setValue(event.channel)
            self.enable_combo.setCurrentText("True" if event.enable else "False")
            self.voltage_spin.setValue(event.voltage)
            self.current_spin.setValue(event.current)

        self.add_field("PSU:", self.psu_idx_combo)
        self.add_field("Channel:", self.channel_spin)
        self.add_field("Enable:", self.enable_combo)
        self.add_field("Voltage:", self.voltage_spin)
        self.add_field("Current:", self.current_spin)

        self.remove_button = QPushButton("Remove Event")
        self.remove_button.setStyleSheet("background-color: #ffcccc; color: #cc0000; font-weight: bold;")
        self.layout.addWidget(self.remove_button)

    def add_field(self, label_text, widget):
        h_layout = QHBoxLayout()
        label = QLabel(label_text)
        h_layout.addWidget(label)
        h_layout.addWidget(widget)
        self.layout.addLayout(h_layout)

    def update_psu_dropdown(self):
        current_idx = self.psu_idx_combo.currentIndex()
        self.psu_idx_combo.clear()
        if not self.psu_config_list:
            self.psu_idx_combo.addItem("No PSUs Loaded (Idx 0)")
        else:
            for idx, psu in enumerate(self.psu_config_list):
                self.psu_idx_combo.addItem(f"PSU {idx}: '{psu.displayName}'")
        if current_idx >= 0 and current_idx < self.psu_idx_combo.count():
            self.psu_idx_combo.setCurrentIndex(current_idx)

    def get_event(self):
        event = SetPSUEvent()
        event.PSUidx = self.psu_idx_combo.currentIndex()
        if event.PSUidx == -1:
             event.PSUidx = 0
        event.channel = self.channel_spin.value()
        event.enable = self.enable_combo.currentText() == "True"
        event.voltage = self.voltage_spin.value()
        event.current = self.current_spin.value()
        return event

class GenericEventWidget(QGroupBox):
    def __init__(self, psu_config_list, event=None, parent=None):
        super().__init__("Event", parent)
        self.layout = QVBoxLayout(self)
        self.psu_config_list = psu_config_list

        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "SetPSUEvent",
            "EvalPSUVoltageEvent",
            "EvalPSUCurrentEvent",
            "EvalPSUPowerEvent"
        ])

        self.type_combo.currentTextChanged.connect(self.build_ui)

        self.dynamic_widget = QWidget()
        self.dynamic_layout = QVBoxLayout(self.dynamic_widget)
        self.dynamic_layout.setContentsMargins(0,0,0,0)

        self.layout.addWidget(QLabel("Event Type:"))
        self.layout.addWidget(self.type_combo)
        self.layout.addWidget(self.dynamic_widget)

        self.remove_button = QPushButton("Remove Event")
        self.remove_button.setStyleSheet("background-color: #ffcccc; color: #cc0000; font-weight: bold;")
        self.layout.addWidget(self.remove_button)

        if event:
            self.type_combo.setCurrentText(event.type)
        self.build_ui(event=event)

    def clear_dynamic_layout(self):
        while self.dynamic_layout.count():
            child = self.dynamic_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                sub_layout = child.layout()
                while sub_layout.count():
                    sub_child = sub_layout.takeAt(0)
                    if sub_child.widget():
                        sub_child.widget().deleteLater()
                sub_layout.deleteLater()

    def add_dynamic_field(self, label_text, widget):
        h_layout = QHBoxLayout()
        label = QLabel(label_text)
        h_layout.addWidget(label)
        h_layout.addWidget(widget)
        self.dynamic_layout.addLayout(h_layout)

    def update_psu_dropdown(self, combo=None):
        if combo is None:
            if hasattr(self, 'psu_idx_combo'):
                combo = self.psu_idx_combo
            else:
                return

        current_idx = combo.currentIndex()
        combo.clear()
        if not self.psu_config_list:
            combo.addItem("No PSUs Loaded (Idx 0)")
        else:
            for idx, psu in enumerate(self.psu_config_list):
                combo.addItem(f"PSU {idx}: '{psu.displayName}'")
        if current_idx >= 0 and current_idx < combo.count():
            combo.setCurrentIndex(current_idx)

    def build_ui(self, text=None, event=None):
        self.clear_dynamic_layout()
        event_type = self.type_combo.currentText()

        self.psu_idx_combo = QComboBox()
        self.update_psu_dropdown(self.psu_idx_combo)

        self.channel_spin = QSpinBox()
        self.channel_spin.setRange(0, 1000)

        self.add_dynamic_field("PSU:", self.psu_idx_combo)
        self.add_dynamic_field("Channel:", self.channel_spin)

        if event:
             self.psu_idx_combo.setCurrentIndex(getattr(event, 'PSUidx', 0))
             self.channel_spin.setValue(getattr(event, 'channel', 0))

        if event_type == "SetPSUEvent":
            self.enable_combo = QComboBox()
            self.enable_combo.addItems(["True", "False"])
            self.voltage_spin = QDoubleSpinBox()
            self.voltage_spin.setRange(0.0, 10000.0)
            self.voltage_spin.setDecimals(3)
            self.current_spin = QDoubleSpinBox()
            self.current_spin.setRange(0.0, 10000.0)
            self.current_spin.setDecimals(3)

            if event and isinstance(event, SetPSUEvent):
                self.enable_combo.setCurrentText("True" if event.enable else "False")
                self.voltage_spin.setValue(event.voltage)
                self.current_spin.setValue(event.current)

            self.add_dynamic_field("Enable:", self.enable_combo)
            self.add_dynamic_field("Voltage:", self.voltage_spin)
            self.add_dynamic_field("Current:", self.current_spin)

        elif event_type == "EvalPSUVoltageEvent":
            self.vlow_spin = QDoubleSpinBox()
            self.vlow_spin.setRange(-10000.0, 10000.0)
            self.vlow_spin.setDecimals(3)
            self.vhigh_spin = QDoubleSpinBox()
            self.vhigh_spin.setRange(-10000.0, 1000000.0)
            self.vhigh_spin.setDecimals(3)
            self.vhigh_spin.setValue(999999.0) # approx inf

            if event and isinstance(event, EvalPSUVoltageEvent):
                self.vlow_spin.setValue(event.VoltageLow)
                if event.VoltageHigh != float('inf'):
                    self.vhigh_spin.setValue(event.VoltageHigh)

            self.add_dynamic_field("Voltage Low:", self.vlow_spin)
            self.add_dynamic_field("Voltage High:", self.vhigh_spin)

        elif event_type == "EvalPSUCurrentEvent":
            self.clow_spin = QDoubleSpinBox()
            self.clow_spin.setRange(-10000.0, 10000.0)
            self.clow_spin.setDecimals(3)
            self.chigh_spin = QDoubleSpinBox()
            self.chigh_spin.setRange(-10000.0, 1000000.0)
            self.chigh_spin.setDecimals(3)
            self.chigh_spin.setValue(999999.0)

            if event and isinstance(event, EvalPSUCurrentEvent):
                self.clow_spin.setValue(event.CurrentLow)
                if event.CurrentHigh != float('inf'):
                    self.chigh_spin.setValue(event.CurrentHigh)

            self.add_dynamic_field("Current Low:", self.clow_spin)
            self.add_dynamic_field("Current High:", self.chigh_spin)

        elif event_type == "EvalPSUPowerEvent":
            self.plow_spin = QDoubleSpinBox()
            self.plow_spin.setRange(-10000.0, 10000.0)
            self.plow_spin.setDecimals(3)
            self.phigh_spin = QDoubleSpinBox()
            self.phigh_spin.setRange(-10000.0, 1000000.0)
            self.phigh_spin.setDecimals(3)
            self.phigh_spin.setValue(999999.0)

            if event and isinstance(event, EvalPSUPowerEvent):
                self.plow_spin.setValue(event.PowerLow)
                if event.PowerHigh != float('inf'):
                    self.phigh_spin.setValue(event.PowerHigh)

            self.add_dynamic_field("Power Low:", self.plow_spin)
            self.add_dynamic_field("Power High:", self.phigh_spin)

    def get_event(self):
        event_type = self.type_combo.currentText()
        if event_type == "SetPSUEvent":
            event = SetPSUEvent()
            event.enable = self.enable_combo.currentText() == "True"
            event.voltage = self.voltage_spin.value()
            event.current = self.current_spin.value()
        elif event_type == "EvalPSUVoltageEvent":
            event = EvalPSUVoltageEvent()
            event.VoltageLow = self.vlow_spin.value()
            vh = self.vhigh_spin.value()
            event.VoltageHigh = float('inf') if vh >= 999998.0 else vh
        elif event_type == "EvalPSUCurrentEvent":
            event = EvalPSUCurrentEvent()
            event.CurrentLow = self.clow_spin.value()
            ch = self.chigh_spin.value()
            event.CurrentHigh = float('inf') if ch >= 999998.0 else ch
        elif event_type == "EvalPSUPowerEvent":
            event = EvalPSUPowerEvent()
            event.PowerLow = self.plow_spin.value()
            ph = self.phigh_spin.value()
            event.PowerHigh = float('inf') if ph >= 999998.0 else ph
        else:
            event = Event()

        if hasattr(self, 'psu_idx_combo'):
            event.PSUidx = max(0, self.psu_idx_combo.currentIndex())
            event.channel = self.channel_spin.value()

        return event

class TestConfigGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)

        self.psu_config_list = []

        # Load Environment Config
        self.env_layout = QHBoxLayout()
        self.load_env_btn = QPushButton("Load EnvironmentConfig JSON")
        self.load_env_btn.clicked.connect(self.load_env_json)
        self.env_layout.addWidget(self.load_env_btn)
        self.main_layout.addLayout(self.env_layout)

        # Load/Save TestSettings
        self.file_buttons_layout = QHBoxLayout()
        self.load_button = QPushButton("Load TestSettings JSON")
        self.load_button.clicked.connect(self.load_json)
        self.save_button = QPushButton("Save TestSettings JSON")
        self.save_button.clicked.connect(self.save_json)
        self.file_buttons_layout.addWidget(self.load_button)
        self.file_buttons_layout.addWidget(self.save_button)
        self.main_layout.addLayout(self.file_buttons_layout)

        # Scrolling Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_container = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_container)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_container)
        self.main_layout.addWidget(self.scroll_area)

        # PSU Settings List
        self.psu_settings_label = QLabel("<b>PSU Setup Phase (PSUSettingsList)</b>")
        self.scroll_layout.addWidget(self.psu_settings_label)

        self.psu_settings_widgets = []

        self.add_psu_setting_btn = QPushButton("Add PSU Setting")
        self.add_psu_setting_btn.clicked.connect(self.add_psu_setting_widget)
        self.scroll_layout.addWidget(self.add_psu_setting_btn)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        self.scroll_layout.addWidget(divider)

        # Event List
        self.events_label = QLabel("<b>Test Sequence Phase (eventList)</b>")
        self.scroll_layout.addWidget(self.events_label)

        self.event_widgets = []

        self.add_event_btn = QPushButton("Add Event")
        self.add_event_btn.clicked.connect(self.add_event_widget)
        self.scroll_layout.addWidget(self.add_event_btn)

    def load_env_json(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Environment Config JSON", "", "JSON Files (*.json)")
        if not filepath:
            return

        try:
            config = EnvironmentConfig()
            config.readJSON(filepath)
            self.psu_config_list = config.PSUConfigList
            self.update_all_psu_dropdowns()
            QMessageBox.information(self, "Success", f"Successfully loaded Environment Config from {os.path.basename(filepath)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load Environment Config JSON:\n{str(e)}")

    def update_all_psu_dropdowns(self):
        for w in self.psu_settings_widgets:
            w.psu_config_list = self.psu_config_list
            w.update_psu_dropdown()
        for w in self.event_widgets:
            w.psu_config_list = self.psu_config_list
            w.update_psu_dropdown()

    def add_psu_setting_widget(self, event=None):
        widget = SetPSUEventWidget(self.psu_config_list, event)
        # Insert before the add button
        idx = self.scroll_layout.indexOf(self.add_psu_setting_btn)
        self.scroll_layout.insertWidget(idx, widget)
        self.psu_settings_widgets.append(widget)
        widget.remove_button.clicked.connect(lambda: self.remove_psu_setting_widget(widget))

    def remove_psu_setting_widget(self, widget):
        self.scroll_layout.removeWidget(widget)
        widget.deleteLater()
        if widget in self.psu_settings_widgets:
            self.psu_settings_widgets.remove(widget)

    def add_event_widget(self, event=None):
        widget = GenericEventWidget(self.psu_config_list, event)
        # Insert before the add event button
        idx = self.scroll_layout.indexOf(self.add_event_btn)
        self.scroll_layout.insertWidget(idx, widget)
        self.event_widgets.append(widget)
        widget.remove_button.clicked.connect(lambda: self.remove_event_widget(widget))

    def remove_event_widget(self, widget):
        self.scroll_layout.removeWidget(widget)
        widget.deleteLater()
        if widget in self.event_widgets:
            self.event_widgets.remove(widget)

    def load_json(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open TestSettings JSON", "", "JSON Files (*.json)")
        if not filepath:
            return

        try:
            settings = TestSettings()
            settings.readJSON(filepath)

            # Clear current
            for w in list(self.psu_settings_widgets):
                self.remove_psu_setting_widget(w)
            for w in list(self.event_widgets):
                self.remove_event_widget(w)

            # Populate
            for psu in settings.PSUSettingsList:
                self.add_psu_setting_widget(psu)
            for event in settings.eventList:
                self.add_event_widget(event)

            QMessageBox.information(self, "Success", f"Successfully loaded TestSettings from {os.path.basename(filepath)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load TestSettings JSON file:\n{str(e)}")

    def save_json(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save TestSettings JSON", "", "JSON Files (*.json)")
        if not filepath:
            return

        try:
            settings = TestSettings()
            for w in self.psu_settings_widgets:
                settings.PSUSettingsList.append(w.get_event())
            for w in self.event_widgets:
                settings.eventList.append(w.get_event())

            settings.writeJSON(filepath)
            QMessageBox.information(self, "Success", f"Successfully saved TestSettings to {os.path.basename(filepath)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save TestSettings JSON file:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Test Config Editor")
    window.resize(600, 800)
    central_widget = TestConfigGUI()
    window.setCentralWidget(central_widget)
    window.show()
    sys.exit(app.exec())