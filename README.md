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

Cerebellum requires Python 3.12+. The core system doesn't require any additional installation, but extra steps are necessary for each of the devices included in the repository:

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

After the checkpoint is passed, Cerebellum will execute the events configured in the Test Config. Each event will report its status, including any pass/fail results or errors during execution. If a fatal error is encountered (e.g. lost connection to a device), the test will abort early. The user can also manually abort the test with the "Stop Test" button. (Note: The Stop command will only take effect at the start of the next event.) Finally, whether the test ended successfully or was prematurely aborted, Cerebellum will shut down all power supplies (i.e. devices that are subclasses of `PowerSupply`).

<!-- Under Construction

## Extending Cerebellum

### Device Specification

Devices: Any device with the module name `Mod` must have two classes inside: `Mod`, representing a controllable instance of the device, and `ModConfig`, representing config data used in the constructor (`__init__`) of `Mod`

### Adding Events

-->
