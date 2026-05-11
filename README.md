# Cerebellum
Cerebellum is a Python project for building and running automated programs on lab equipment, with a focus on extensibility and ease-of-use. At its core, Cerebellum is based on "devices" - power supplies, microcontrollers, oscilloscopes, etc. - and "events", containing commands for these devices. The complex coding and libraries behind these objects are manipulated through a user-friendly GUI, and the system can be easily extended with new devices and events.

### Features
Currently, Cerebellum supports the following devices:

- SCPI Power Supplies
- CAEN Power Supplies
- ETL Readout Boards

Cerebellum features a high degree of extensibility. Any new device can be integrated with the modification of just two Python files - the system will automatically 
incorporate the new device and its events, including the generation of custom GUI units.

### Motivation - High Luminosity LHC
From 2026 to 2030, CERN's Large Hadron Collider (LHC) will halt all experiments to allow for routine maintenance and new additions. One of the central goals of this intermission is the High Luminosity upgrade, which will increase the number of particles coursing through the LHC by a factor of 10 and result in a 2-3x higher particle collision rate. To handle this improved collision rate, the Compact Muon Solenoid (CMS), one of the detector stations on the LHC, will need additional sensors for recording the timing of collisions. These sensors will output immense quantities of data, which must be aggregated by Readout Boards (RBs) and sent via fiber-optic cable to a database for future processing.

Led by Dr. Frank Geurts, the Rice Heavy Ion Group at Rice University's Department of Physics and Astronomy will be responsible for verifying the functionality of a portion of these RBs before they are sent to CERN for installation. Accordingly, Dr. Geurts recruited a team of senior undergraduates through Rice's Senior Design program to help him in his efforts, and part of this team's solution is the Cerebellum automated testing software.

Cerebellum was originally designed for verifying RBs; setting power supplies, reading data from the RB, and returning with a pass/fail. However, Cerebellum is by no means limited to this use case. Any user can easily extend the software for their own needs and streamline their lab environment.

### Installation
Start by cloning the source code into a local directory. _A pre-compiled installation is intended for future development._

```
git clone https://github.com/MatthewNutt5/Cerebellum.git
```

Cerebellum requires Python 3.7+. The GUI uses the PySide6 module, which can be installed through pip:

```
pip install pyside6
```

Extra steps are also necessary for each of the devices included in the repository; skip any you do not wish to use.

> **NOTE:**  The specific selection of libraries for Cerebellum may impart additional constraints on the required Python interpreter version.

#### `SCPIPowerSupply`
The libraries for `SCPIPowerSupply` can be installed through pip. (Additionally, installing `pyserial` will permit the GUI to automatically populate any device field named `com` with a dropdown of available COM ports.)

```
pip install pyserial socketscpi
```

#### `CAENPowerSupply`
First install the C library from the [CAEN website](https://www.caen.it/products/caen-hv-wrapper-library/), then install the Python bindings through pip:

```
pip install caen-libs
```

#### `TamaleroReadoutBoard`
The version of the interface currently used to control readout boards comes from [Tao Huang's fork](https://gitlab.cern.ch/tahuang/module_test_sw) of the Tamalero software. Follow the instructions in that repository, but instead of cloning the master branch, clone the `RBF6v1_RiceTestBoard` branch:

```
git clone -b RBF6v1_RiceTestBoard https://gitlab.cern.ch/tahuang/module_test_sw.git
```

You will also need to `cd` into the repository and run `source setup.sh` in order to set up environment variables at the start of each terminal session.

## Using Cerebellum

To launch the Cerebellum GUI, run `/Cerebellum/GUI/MainGUI.py` with Python. _A simplified executable is intended for future development._

```
python3 ./Cerebellum/GUI/MainGUI.py
```

### Configuring Devices

In the "Environment Config" GUI tab, press the "Add Device Config" button at the bottom to add a new device. Once the config has been added, use the dropdown menu at the top of the config to select which device to configure (e.g. `SCPIPowerSupply`, `TamaleroReadoutBoard`). When a device type is selected, the config box will update with its corresponding configuration fields (e.g. IP address, COM port). Fill out the fields with the environment's information, and the device will be ready for use.

Configurations can be saved in a JSON file with the "Save JSON" button, and later loaded with the "Load JSON" button. Since the GUI resets when closed, this is necessary for preserving any existing configurations.

### Building a Program

Next, in the "Test Config" GUI tab, press the "Add Event" button at the bottom to add a new event. As with devices, a dropdown menu at the top of each event is used to select the event type, and the event's fields can then be filled in. Any event that uses a device will have a "Device Index" field that is automatically populated with a dropdown menu containing the currently-configured devices. This helps with matching events to devices - if there is a mismatch, it will be reported in a verification step later.

Test programs can also be saved/loaded with JSON files.

### Running the Program

Finally, in the "Run Test" GUI tab, press the "Start Test" button to initiate the test currently configured in the GUI. The test will begin in a subprocess that will report its output to the GUI. First, Cerebellum will initialize its device types and report any malfunctions (e.g. if a device is unavailable due to missing libraries). Then, it will verify the event list, checking that every event uses the correct device type, and connect to all configured devices. Cerebellum will then pause to let the user check device credentials - press Enter in the input box at the bottom of the window to continue.

After the checkpoint is passed, Cerebellum will execute the events configured in the Test Config. Each event will report its status, including any pass/fail results or errors during execution. If a fatal error is encountered (e.g. lost connection to a device), the test will abort early. The user can also manually abort the test with the "Stop Test" button. (Note: The Stop command will only take effect at the start of the next event.) Finally, whether the test ended successfully or was prematurely aborted, Cerebellum will shut down all devices - some device implementations may ignore this step, if there is nothing to "shut down" remotely, but for example, power supplies will turn off all of their channels.

## Extending Cerebellum

As previously mentioned, Cerebellum has been designed with dynamic importing and a procedural GUI to automate the process of integrating new devices and events. Extending Cerebellum only requires the addition of a device specification file and events to use the device.

### Device Specification

In Cerebellum, "devices" are physical tools that can be controlled remotely - power supplies, microcontrollers, oscilloscopes, etc. All devices offer simple functions for control while handling initialization, communication protocol, message format, etc. internally. These functions are later called by "events" to carry out more complicated commands (see [below](#events)).

Let's say you want to add a new device, called "ExampleDevice". In the `Cerebellum.Device` submodule , make a new file, `ExampleDevice.py`. This is where the device specification will be written. In the file, create two classes: `ExampleDeviceConfig`, extending `DeviceConfig`, and `ExampleDevice`, extending `Device`. The device class `ExampleDevice` represents a controllable instance of the device with public methods for calling commands, and the configuration class `ExampleDeviceConfig` represents configuration data used in the constructor (`__init__`) of `ExampleDevice`.

For example, the `SCPIPowerSupply` device class offers `set_voltage()`, `enable_channel()`, etc., which can be used to control the physical power supply. Accordingly, `SCPIPowerSupplyConfig` has fields for the IP address, COM port, etc. for connecting to said power supply.

Refer to the existing implementations for examples of how to write new devices. Some important notes:

- The naming convention of `<Device Name>.py` containing `<Device Name>` and `<Device Name>Config` *must* be followed, or the automatic import system will not work.
- Every device must implement: an initialization routine (using the corresponding DeviceConfig), a delete routine (for disconnecting from the device), an ID-retrieval function, and a shutdown function - though it may suffice to do nothing in some of these functions, depending on how the device behaves.
- The `__init__()` function of a `DeviceConfig` must include the `vars_dict` parameter, which is used by the JSON read/write system to store configs. Again, see existing implementations for examples, and ideally, copy/paste an existing `__init__()` as a skeleton for a new one.
- The instance attributes of a `DeviceConfig` represent the parameters of an individual configuration, but class attributes can be used to generate the GUI for the config. For any instance attribute `field`, the class attribute `field_title` contains a string representing the field's label in the GUI (e.g. `ip` --> `ip_title = "IP Address"`), and the class attribute `field_options` contains a list of options to offer the user (e.g. `baudrate` --> `baudrate_options = [2400, 4800, ...]`).
- Abstract interfaces can be used to generalize the device, such as `SCPIPowerSupply` and `CAENPowerSupply` both being children of `PowerSupply` and sharing the same public methods for control. This also allows for general events - `SetPSU` can act on any subclass of `PowerSupply`.

### Events

"Events" in Cerebellum specify commands that are carried out during execution. Each event can use any arbitrary command, such as `Sleep` using `time.sleep()` to delay the program, but events can also call upon device commands - `SetPSU` uses the `set_voltage()` and `set_current()` methods from `PowerSupply`. Events are (currently) stored in the monolithic `Event.py` file (from the core `Cerebellum` module), and new events are written in much the same way as devices.

After adding `ExampleDevice`, let's say you want to add a new event, called "DoStuff", to make use of the device's commands. In `Event.py`, first write a new abstract class, called `ExampleDeviceEvent`. This event represents any event that makes use of `ExampleDevice`, and should include any functionality that is common to `ExampleDevice` - for instance, `PowerSupplyEvent` includes the `self.channel` attribute, since it is used in all power supply events.

`DoStuff` can then be written as a class that extends `ExampleDeviceEvent`. This event's `exec()` function will be called when its turn arrives during execution; this is where the actual functionality of `DoStuff` should be written.

Again, refer to the existing implementations for examples of how to write new events. Some important notes:

- Unlike devices, there is no required naming convention for events.
- Every event must implement a constructor and an `exec()` function. As mentioned above, the `exec()` function is called during test execution - accordingly, the `exec()` of `DeviceEvent`s input active `Device`s for use during the test.
- As with `DeviceConfig`s, the `__init__()` function of an event must include the `vars_dict` parameter. Additionally, it is recommended to call `super().__init__()` as part of the non-`vars_dict` initialization, in order to set up common instance attributes; every `DeviceEvent` uses `self.device_idx`, for example.
- All abstract device events (`ExampleDeviceEvent`) must additionally implement the `verify()` function. This function is used during the verification stage of test execution to ensure that each event refers to the correct device, catching any incorrect assignments before they appear during event execution.
- If an event does not require any device (such as `Sleep` or `Checkpoint`), it extends from the root `Event` class (and does not require the `verify()` function).
- As with `DeviceConfig`s, instance attributes contain parameters for each event, and class attributes are used for generating the GUI. See [above](#device-specification).
