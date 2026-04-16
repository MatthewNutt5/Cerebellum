# Cerebellum
Cerebellum is a Python project for building and running automated programs on lab equipment, with a focus on extensibility and ease-of-use. At its core, Cerebellum is based on "devices" - power supplies, microcontrollers, oscilloscopes, etc. - and "events", specifying commands to send to these devices. The complex coding and libraries behind these objects are manipulated through a user-friendly GUI.

### Features
Currently, Cerebellum supports the following devices:

- SCPI Power Supplies
- CAEN Power Supplies
- LHC CMS ETL Readout Boards

Cerebellum features a high degree of extensibility. Any new device can be integrated with the modification of just two Python files - the system will automatically 
incorporate the new device and its events, including custom GUI units.

### Motivation - High Luminosity LHC
From 2026 to 2030, CERN's Large Hadron Collider (LHC) will halt all experiments to allow for routine maintenance and new additions. One of the central goals of this shutdown is the High Luminosity upgrade, which will increase the number of particles coursing through the LHC by a factor of 10 and result in a 2-3x higher particle collision rate. To handle this improved collision rate, the Compact Muon Solenoid (CMS), one of the detector stations on the LHC, will need additional sensors for recording the timing of collisions. These sensors will output immense quantities of data, which must be aggregated by Readout Boards (RBs) and sent via fiber to a database for future processing.

Led by Dr. Frank Geurts, the Rice Heavy Ion Group at Rice University's Department of Physics and Astronomy will be responsible for verifying the functionality of these RBs before they are sent to CERN for installation. Accordingly, Dr. Geurts recruited a team of senior undergraduates through Rice's Senior Design program to help him in his efforts, and part of this team's solution is the Cerebellum automated testing software.

Cerebellum was originally designed for verifying RBs; setting power supplies, reading data from the RB, and returning with a pass/fail. However, Cerebellum is by no means limited to this use case. Any user can easily extend the software for their own needs and streamline their lab environment.

<!-- Under Construction

## Using Cerebellum

### Installation

### Configuring Devices

### Building a Program

## Extending Cerebellum

### Device Specification

Devices: Any device with the module name `Mod` must have two classes inside: `Mod`, representing a controllable instance of the device, and `ModConfig`, representing config data used in the constructor (`__init__`) of `Mod`

### Adding Events

-->
