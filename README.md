# Cerebellum
Cerebellum is a Python project for building and running automated programs on lab equipment, with a focus on extensibility and ease-of-use. At its core, Cerebellum is based on "devices" - power supplies, microcontrollers, oscilloscopes, etc. - and "events", containing commands for these devices. The complex coding and libraries behind these objects are manipulated through a user-friendly GUI, and the system can be easily extended with new devices and events.

### Features
Currently, Cerebellum supports the following devices:

- SCPI Power Supplies
- CAEN Power Supplies
- LHC CMS ETL Readout Boards

Cerebellum features a high degree of extensibility. Any new device can be integrated with the modification of just two Python files - the system will automatically 
incorporate the new device and its events, including the generation of custom GUI units.

### Motivation - High Luminosity LHC
From 2026 to 2030, CERN's Large Hadron Collider (LHC) will halt all experiments to allow for routine maintenance and new additions. One of the central goals of this intermission is the High Luminosity upgrade, which will increase the number of particles coursing through the LHC by a factor of 10 and result in a 2-3x higher particle collision rate. To handle this improved collision rate, the Compact Muon Solenoid (CMS), one of the detector stations on the LHC, will need additional sensors for recording the timing of collisions. These sensors will output immense quantities of data, which must be aggregated by Readout Boards (RBs) and sent via fiber-optic cable to a database for future processing.

Led by Dr. Frank Geurts, the Rice Heavy Ion Group at Rice University's Department of Physics and Astronomy will be responsible for verifying the functionality of a portion of these RBs before they are sent to CERN for installation. Accordingly, Dr. Geurts recruited a team of senior undergraduates through Rice's Senior Design program to help him in his efforts, and part of this team's solution is the Cerebellum automated testing software.

Cerebellum was originally designed for verifying RBs; setting power supplies, reading data from the RB, and returning with a pass/fail. However, Cerebellum is by no means limited to this use case. Any user can easily extend the software for their own needs and streamline their lab environment.

### Installation
Start by cloning the source code into a local directory. _Future plans include a pre-compiled installation._

```
git clone https://github.com/MatthewNutt5/Cerebellum.git
```

Cerebellum requires Python 3.12+. The core system doesn't require any additional installation, but extra steps are necessary for each of the devices included in the repository:

#### `SCPIPowerSupply`
The libraries for `SCPIPowerSupply` can be installed through pip:

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

<!-- Under Construction

## Using Cerebellum

### Configuring Devices

### Building a Program

## Extending Cerebellum

### Device Specification

Devices: Any device with the module name `Mod` must have two classes inside: `Mod`, representing a controllable instance of the device, and `ModConfig`, representing config data used in the constructor (`__init__`) of `Mod`

### Adding Events

-->
