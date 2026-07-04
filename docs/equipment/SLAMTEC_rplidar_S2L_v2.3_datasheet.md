# SLAMTEC RPLIDAR S2L v2.3

## Introduction
The RPLIDAR S2L is a next-gen cost effective 360 degree 2D laser scanner (LiDAR). It has the capability of taking up to 32k samples of laser ranging per second with a high rotation speed of 10Hz. Unlike traditional LiDARs, this scanner is equipped with contactless power and signal transmission technology, which allows it to operate in a stable perfomance for a longer time. It can perform a 2D 360 degree scan within a range of 18 meters and procude a 2D point cloud map of the space. Currently, the RPLIDAR S2L is being used in a variety of applications, including robotics, autonomous vehicles, and mapping.

This scanner has the ability to detect object in long distances compared to other RPLIDAR series. Additionally, it can detect objects in white and black colors, and objects under direct sunlight. 

This scanner typical scanning frequency is 10Hz (600 RPM). With this frequency, the scanner's sample rate is 32kHz, and the angular resolution is 0.1125°. 

## System Composition and Connection
The RPLIDAR S2L consists of range scanner core and the mechanical powering system that allows the scanner's core to rotate at a high speed. Under normal operation, the core will rotate and scan clockwise. This scanner comes with a rotation speed detection and adative system that manages automatically the angular resolution based on the rotation speed. If the actual rotation speed of the scanner is required, the host system can retrive the related data via the communication interface. 

### Mechanism 
The RPLIDAR S2L is based on the laser flight-of-time (TOF) ranging principle and adopts the high speed laser acquisition and processing hardware that was developed by SLAMTEC. During the ranging process the RPLIDAR emits a modulated infrared laser signal. The signal is then reflected by an object and the RPLIDAR detects the returning signal. The return signal is then sampled by the laser acquisition system of the RPLIDAR, and is processed by the embedded processor which then outputs the distance value and and angle value between the object and the RPLIDAR via the communication interface. 

When the scanner is driven by the motor system, the range scanner core will rotate clockwise and it will perform the 360 degree scan for the current environment. 

### Safety and Scope

This range scanner using a low-power infrared laser as its light source and drives using a modulated pulse. The emitted infrared light in a very short time frame that according the products data sheet ensures complanance with 21 CFR 1040.10 and 1040.11 except for deviation pursuant to Laser No. 50, dated jun 24, 2007. Caution is advsise: Use of controls or adjustments or performance of procedures other than those specified herein may result in hazadous radiation exposure. 

### Data Ouput

The operation the RPLIDAR output will be communicated via its communication interface. Each sample point data per frame contains the following information

| Data Type | Unit | Description|
|:----------|:-----|:-----------|
| Distance Value| mm            | Current measured distance value between the RPLIDAR's rotating core and the sample point|
| Angle         | Degree        | Angle of the current sample point relative to the orientation of the RPLIDAR|
| Start Signal  | Boolean value | Flag of new scann |
| Checksum      |     -         | Checksum of the data returned by the RPLIDAR| 

For specific data format, refer to the "EXPRESS_SCAN Command Request and Response Data Formate" in the S2L Communication Protocal 


<img src="/docs/images/RPLIDAR_sample_point_data_frames.png" alt="SLAMTEC RPLIDAR S2L Sample Point Data Frames" style="width:600px">

The output sample data is continuous, and it contains the sample point data frames above. The output format can be configured by the host system. Additionaly, output can be stop by the host system if desired by sending a control command.

For the specific
operation, refer to the S2 S2L Communication Protocol or contact SLAMTEC.

## High-Speed Sampling Protocol and its Compatibility
Update is required for the matched SDK or modify the original driver and use DenseBoost in the high-speed sampling protocol for the 32k times per second mode of the RPLIDAR S2L. 


## Application Scenarios
This system can be used in the following scenarios:
- General simulataneous localization and mapping (SLAM)
- Environment scanning and 3D re-modeling
- Service robots or industrial robots working for long hours
- Navigation and localization of home service/clearning robots
- General robot navigation and localization
- Localization and obstacle avoidance of smart toys
  
## Measurement Performance
| Item             | Unit            | Min  | Typical         | Max | Remarks             |
|:-----------------|:----------------|:-----|:----------------|:----|:--------------------|
|Working Wavelength| Nanometer (nm)  | 895  | 905             | 915 | Infrared Light Band |
|Laser Power       | Watts (W)       | -    | 25              | -   | Peak power          |
|Pulse Length      | Nanosecond (ns) | -    | 5               | -   | -                   |
|Laser Safety Class| -               | -    |IEC-60825 Class 1| -   | -                   |

Note: The value of the laser power annotated above is for continuous light emission, and the actual avg power will be much lower.


## Optical Window
To allow the RPLIDAR S2L to function properly, ensure that there is enough space for the device to emit and receive during the designment phase of the host system. If the optical window is blocked it will impair the functionality and performance resolution of the scanner. 

## Coordinate System Definition of Scanning Data
<img src="/docs/images/RPLIDAR_scanning_data_coord_sys_def.png" alt="SLAMTEC RPLIDAR S2L Scanning Data Coordinate System Definition" style="width:600px">

This scanner uses a left-handed coordinate system . The dead ahead of the sensor is the x-axis of the coordinate system. The origin is located at the center of the scanner's rotating core. The rotation angle is designed to increased as the device rotates clockwise. 

## Communication Interface
This scanner uses a separate  5V DC power supply to power the ranging system and motor system. 
It is standard for the RPLIDAR S2L to use a XH2.54-5P male connector for the communication interface. 

<img src="/docs/images/RPLIDAR_comms_interface_connector.png" alt="SLAMTEC RPLIDAR S2L Communication Interface Connector" style="width:600px">

The pinout of the communication interface is as follows:

| Color | Signal Name | Type | Description | Min (V) | Typical (V) | Max (V) |
|:-----|:------------|:-----|:------------|:--------|:------------|:----|
|Red   | VCC         | Power| 5V DC power supply for the RPLIDAR S2L | 4.9 | 5.0 | 5.2 |
|Yellow| TX          | Output| Serial port output of scanner core | 0.0 | / | 3.5 |   
|Green | RX          | Input | Serial port input of scanner core | 0.0 | / | 3.5 | 
|Black | GND         | Power | Ground of the RPLIDAR S2L | 0.0 | 0.0 | 0.0 |
|Blue  | NC          | /     | Advise grounding          | - | - | - |

### Power Supply Interface
The RPLIDAR S2L uses a separate 5V DC power supply to power the range scanner core and motor system. To ensure proper operation, the host system needs to ensure the output of the power supply meets its requirement of the power supply ripple. 

|Item | Unit | Min | Typical | Max | Remarks |
|:---|:----|:---|:-------|:---|:-------|
|Power Voltage | V | 4.9 | 5.0 | 5.2 | If not enough voltage is supplied, the measurement accuracy may be affected. |
|Power Supply Ripple | mV | - | - | 150 | Excessive power supply noise may affect the measurement accuracy of the scanner. |
|System Start Current | mA | - | 1500 | - | The systems startup requires a higher current than the normal operation. If the power supply cannot provide enough current, the system may not start properly. |
|Power Supply Current | mA | - | 500 | 600 | - | 

*Note: The power supply current is the average current of the RPLIDAR S2L during normal operation. The actual current may be higher than the average value, especially when the system is starting up. The host system needs to ensure that the power supply can provide enough current for the RPLIDAR S2L to operate properly.*

### Data Communication Interface
The RPLIDAR S2L takes the 3.3V TTL serial port as its data communication interface. 

The table below shows the transmission speed and protocol stadard of the RPLIDAR S2L:

| Item | Unit | Min | Typical | Max | Remarks |
|:----|:----|:---|:-------|:---|:-------|
| Baud Rate | M | - | 1 | - | - |
| Working Mode | - | - | 8 data bits, 1 stop bit, no parity | - | - | - |
| Output High Voltage | V | 2.9 | 3.3 | 3.5 | Output signal with high voltage |
| Output Low Voltage | V | 0.0 | 0.0 | 0.4 | Output signal with low voltage |
| Input High Voltage | V | 2.4 | 3.3 | 3.5 | Input signal with high voltage |
| Input Low Voltage | V | 0.0 | 0.0 | 0.4 | Input signal with low voltage |

### Scanner Motor Control 
User can change the rotation speed of the scanner by sending a control command to the RPLIDAR S2L. The scanner's motor cannot start or stop on its own, and its working state will depend on the laser scan command sent by the host system. 

## Self Protection and Status Detection
The RPLIDAR S2L has a self-protection mechanism that can detect the status of the scanner to avoid it from being damaged. To avoid damage the scanner will shut itself down if any of the following conditions are detected:
- The scan speed of the laser scanner system is unstable
- The scan speed of the laser scanner system is too low
- The laser signal senser works abnormally

The host system can retrieve the status of the scanner system via the communication interface, and restart the scanner system to try to recover work from errors. 