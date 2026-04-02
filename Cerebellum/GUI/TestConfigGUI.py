"""
Placeholder
"""

from Cerebellum.TestConfig import TestConfig
import Cerebellum.Event
from Cerebellum.Event import Event
from Cerebellum.Device.Device import DeviceConfig

from PySide6.QtWidgets import  (QApplication, QMainWindow,
                                QWidget, QScrollArea, QGroupBox, QVBoxLayout, QHBoxLayout,
                                QPushButton, QFileDialog, QMessageBox, QLabel,
                                QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox, QLineEdit)
from PySide6.QtCore import Qt

from typing import Any
from contextlib import contextmanager
import inspect, sys, os, logging

# Find all events in Event that have a valid constructor
# Create a dict of [event class name, event constructor]
EVENTS: dict[str, Any] = {}
for member_name, member in inspect.getmembers(Cerebellum.Event):
    if inspect.isclass(member):
        try:
            _ = member()
            # The ABC class is used for abstract interfaces; it should not be included
            if (member_name != "ABC"):
                EVENTS[member_name] = member
        except:
            pass



# Logging handler and context manager to capture logging messages during an operation
class BufferedLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.buffer: list[str] = []

    def emit(self, record):
        self.buffer.append(self.format(record))

@contextmanager
def capture_warnings():
    handler = BufferedLogHandler()
    handler.setLevel(logging.WARNING)
    handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

    logging.getLogger().addHandler(handler)
    try:
        yield handler.buffer
    finally:
        logging.getLogger().removeHandler(handler)



class EventWidget(QGroupBox):

    def __init__(self, event: (Event | None) = None, parent = None):

        super().__init__("Event", parent)
        self.main_layout = QVBoxLayout(self)

        # Use available constructors as choices for the Event class
        self.event_class_edit = QComboBox()
        self.event_class_edit.setEditable(False)
        self.event_class_edit.addItems(list(EVENTS.keys()))

        # Ignore wheelEvents so that scrolling will only ever scroll the list of events
        self.event_class_edit.wheelEvent = (lambda event: event.ignore())

        self.main_layout.addWidget(self.event_class_edit)

        # Init event selection to event class if given
        if event:
            self.event_class_edit.setCurrentText(event.__class__.__name__)

        # Store all field edits in a dict to retrieve field data
        # Store all field widgets (label + edit) in a list that can be cleared
        self.field_edits: dict[str, QWidget] = {}
        self.field_widgets: list[QWidget] = []

        # Add the remove button widget
        # NOTE: Never delete this widget, only add/remove it from the *layout* when updating
        # This way, it remains connected to the parent GUI
        self.remove_button = QPushButton("Remove Event")
        self.remove_button.setStyleSheet("background-color: #ffcccc; color: #cc0000; font-weight: bold;")

        # Update event select to open up fields and allow for data population
        # This populates field_edits with field names and corresponding widgets
        # Also re-run this update any time the event selection changes
        self._update_event_select()
        self.event_class_edit.currentTextChanged.connect(self._update_event_select)

        # Populate with data if provided
        # Type conversions should only be necessary for QComboBox
        # Need a special case here for extracting device_idx
        if event:
            for field_name, field_edit in self.field_edits.items():
                field_value = vars(event)[field_name]
                if isinstance(field_edit, QComboBox):
                    field_edit.setCurrentText(str(field_value))
                elif isinstance(field_edit, QCheckBox):
                    field_edit.setChecked(bool(field_value))
                elif isinstance(field_edit, QSpinBox):
                    field_edit.setValue(int(field_value))
                elif isinstance(field_edit, QDoubleSpinBox):
                    field_edit.setValue(float(field_value))
                elif isinstance(field_edit, QLineEdit):
                    field_edit.setText(str(field_value))

    

    def get_event(self) -> Event:
        
        # First, retrieve an Event instance from the current selected event class
        event_class_name = self.event_class_edit.currentText()
        constructor = EVENTS[event_class_name]
        blank_event = constructor()

        # Make a dict for the config based on the current values from edits
        config_dict: dict[str, Any] = {}
        for field_name, field_edit in self.field_edits.items():
            
            # Get the field value according to the edit type
            if isinstance(field_edit, QComboBox):
                field_value = field_edit.currentText()
            elif isinstance(field_edit, QCheckBox):
                field_value = field_edit.isChecked()
            elif isinstance(field_edit, (QSpinBox | QDoubleSpinBox)):
                field_value = field_edit.value()
            elif isinstance(field_edit, QLineEdit):
                field_value = field_edit.text()
            else:
                field_value = 0
            
            # Convert the field value according to the type in the blank_event
            field_type = type(getattr(blank_event, field_name))
            config_dict[field_name] = field_type(field_value)
        
        # Return an Event corresponding to the selected class, populated
        # with the data extracted from the edits
        return constructor(vars_dict=config_dict)



    # def update_devices(self, device_config_list: list[DeviceConfig]) -> None:

    #     # If this event requires a device_idx, update the options
    #     if ("device_idx" in self.field_edits):



    def _add_field(self, label_text: str, edit: QWidget) -> None:
        h_layout = QHBoxLayout()
        label = QLabel(label_text)
        h_layout.addWidget(label)
        h_layout.addWidget(edit)
        h_layout.setAlignment(label, Qt.AlignmentFlag.AlignLeft)
        h_layout.setAlignment(edit, Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addLayout(h_layout)
        self.field_widgets.append(label)
        self.field_widgets.append(edit)



    def _update_event_select(self) -> None:

        # First, retrieve an Event instance from the current selected event class
        event_class_name = self.event_class_edit.currentText()
        constructor = EVENTS[event_class_name]
        blank_event = constructor()

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
        for field_name, field_value in vars(blank_event).items():
            # First check if the field has a corresponding _options class attribute
            # If so, construct the field_edit as a ComboBox, and set the options as such
            # Otherwise, construct according to the field's type (e.g. LineEdit, SpinBox, etc.)
            # Also set the current text/value to the default text/value
            if (field_name + "_options") in dir(blank_event.__class__):
                field_edit = QComboBox()
                field_edit.setEditable(False)
                items = [str(item) for item in getattr(blank_event, field_name + "_options")]
                field_edit.addItems(items)
                field_edit.setMinimumContentsLength(len(max(items, key=len)) + 3)
                field_edit.setCurrentText(str(field_value))
            # Bool has to be checked before int because it is a child of int
            elif isinstance(field_value, bool):
                field_edit = QCheckBox()
                field_edit.setChecked(bool(field_value))
            elif isinstance(field_value, int):
                field_edit = QSpinBox()
                field_edit.setRange(-2147483648, 2147483647)
                field_edit.setValue(int(field_value))
            elif isinstance(field_value, float):
                field_edit = QDoubleSpinBox()
                field_edit.setDecimals(6)
                field_edit.setRange(float("-inf"), float("inf"))
                field_edit.setValue(float(field_value))
                field_edit.setMinimumWidth(100)
            else:
                field_edit = QLineEdit()
                field_edit.setText(str(field_value))
                
            # # Special case
            # # If a field is called "device_idx", overwrite the widget with a ComboBox that retrieves all current Devices
            # # The updating is done in a separate function
            # if (field_name == "device_idx"):
            #     field_edit = QComboBox()
            #     field_edit.setEditable(True) # Set editable so that the field won't ignore a loaded value
            #     items = [port.name for port in serial.tools.list_ports.comports()]
            #     field_edit.addItems(items)
            #     field_edit.setMinimumContentsLength(len(max(items, key=len)) + 3)
            #     field_edit.setCurrentText(str(field_value))

            # Ignore wheelEvents so that scrolling will only ever scroll the list of configs
            field_edit.wheelEvent = (lambda event: event.ignore())

            # Update the layout with the new field
            # If the field has a corresponding _title class attribute, use that as the label
            # Otherwise, just use the field name
            if (field_name + "_title") in dir(blank_event.__class__):
                self._add_field(getattr(blank_event, field_name + "_title"), field_edit)
            else:
                self._add_field(field_name, field_edit)

            # Update the dict of field edits
            self.field_edits[field_name] = field_edit

        # Add the remove button back to the layout
        self.main_layout.addWidget(self.remove_button)



class TestConfigGUI(QWidget):

    def __init__(self):

        super().__init__()
        self.main_layout = QVBoxLayout(self)

        # # Load Environment Config
        # self.env_layout = QHBoxLayout()
        # self.load_env_btn = QPushButton("Load EnvironmentConfig JSON")
        # self.load_env_btn.clicked.connect(self.load_env_json)
        # self.env_layout.addWidget(self.load_env_btn)
        # self.main_layout.addLayout(self.env_layout)

        # Load/save buttons
        # Connect to load/save methods
        self.file_buttons_layout = QHBoxLayout()
        self.load_button = QPushButton("Load JSON")
        self.load_button.clicked.connect(self._load_json)
        self.save_button = QPushButton("Save JSON")
        self.save_button.clicked.connect(self._save_json)
        self.file_buttons_layout.addWidget(self.load_button)
        self.file_buttons_layout.addWidget(self.save_button)
        self.main_layout.addLayout(self.file_buttons_layout)

        # Event scrollable list area
        self.event_scroll_area = QScrollArea()
        self.event_scroll_area.setWidgetResizable(True)
        self.event_container = QWidget()
        self.event_layout = QVBoxLayout(self.event_container)
        self.event_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.event_scroll_area.setWidget(self.event_container)
        self.main_layout.addWidget(QLabel("Events:"))
        self.main_layout.addWidget(self.event_scroll_area)

        # "Add Event" button
        self.add_event_button = QPushButton("Add Event")
        self.add_event_button.clicked.connect(self._add_event_widget)
        self.main_layout.addWidget(self.add_event_button)

        # Store all event widgets in a list that can be cleared
        self.event_widgets: list[EventWidget] = []



    def get_test_config(self) -> TestConfig:
        config = TestConfig()
        for widget in self.event_widgets:
            config.event_list.append(widget.get_event())
        return config



    # def load_env_json(self):
    #     filepath, _ = QFileDialog.getOpenFileName(self, "Open Environment Config JSON", "", "JSON Files (*.json)")
    #     if not filepath:
    #         return

    #     try:
    #         config = EnvironmentConfig()
    #         config.read_json(filepath)
    #         self.psu_config_list = config.PSUConfigList
    #         self.update_all_psu_dropdowns()
    #         QMessageBox.information(self, "Success", f"Successfully loaded Environment Config from {os.path.basename(filepath)}")
    #     except Exception as e:
    #         QMessageBox.critical(self, "Error", f"Failed to load Environment Config JSON:\n{str(e)}")

    # def update_all_psu_dropdowns(self):
    #     for w in self.psu_settings_widgets:
    #         w.psu_config_list = self.psu_config_list
    #         w.update_psu_dropdown()
    #     for w in self.event_widgets:
    #         w.psu_config_list = self.psu_config_list
    #         w.update_psu_dropdown()



    def _add_event_widget(self, event: (Event | None) = None) -> None:
        widget = EventWidget(event)
        self.event_layout.addWidget(widget)
        self.event_widgets.append(widget)
        widget.remove_button.clicked.connect(lambda: self._remove_event_widget(widget, True))



    def _remove_event_widget(self, widget: EventWidget, update: bool) -> None:
        self.event_layout.removeWidget(widget)
        widget.deleteLater()
        if update:
            self.event_widgets.remove(widget)



    def _load_json(self) -> None:
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Test Config JSON", "", "JSON Files (*.json)")
        if not filepath:
            return

        try:

            with capture_warnings() as warnings:

                config = TestConfig()
                config.read_json(filepath)

                # Clear current UI
                for widget in self.event_widgets:
                    self._remove_event_widget(widget, False)
                self.event_widgets.clear()

                # Populate UI
                for event in config.event_list:
                    self._add_event_widget(event)

            if warnings:
                string = "Warnings encountered while loading configuration file:"
                for warning in warnings:
                    string += f"\n{warning}"
                QMessageBox.warning(self, "Warning", string)
            else:
                QMessageBox.information(self, "Success", f"Successfully loaded configuration file.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load configuration file:\n{e}")



    def _save_json(self) -> None:
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Test Config JSON", "", "JSON Files (*.json)")
        if not filepath:
            return

        try:
            self.get_test_config().write_json(filepath)
            QMessageBox.information(self, "Success", f"Successfully saved configuration file.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration file:\n{e}")



# Run the GUI as a standalone window
def testGUI() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Test Config Editor")
    window.resize(600, 800)
    central_widget = TestConfigGUI()
    window.setCentralWidget(central_widget)
    window.show()
    sys.exit(app.exec())
