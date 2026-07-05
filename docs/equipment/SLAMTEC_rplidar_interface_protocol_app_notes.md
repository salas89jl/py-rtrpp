# RPLIDAR S2L Communication Protocol Application Notes

This document contains the communication protocol and application notes derived from the SLAMTEC RPLIDAR Interface Protocol and Application Notes provided by SLAMTEC. The notes found on this page are only intended to provide a brief overview of the RPLIDAR S2L communication protocol and its application. For more detailed information, please refer to the official SLAMTEC documentation.

<a href="https://bucket-download.slamtec.com/6494fd238cf5e0d881f56d914c6d1f355c0f582a/LR001_SLAMTEC_rplidar_protocol_v2.4_en.pdf" target="_blank">Interface Protocol and Application Notes</a>


## Overview
Communication between the host system and the RPLIDAR S2L is established via the TTL UART serial interface. The host system can retrive scan data, device status, and other information from the RPLIDAR S2L by sending commands to the device. The RPLIDAR S2L will respond to the host system with the requested data or status information. For informatin about the bottom layer communication protocol and the electrical level definition of the serial signal used for communication, please refer to the SLAMTEC RPLIDAR S2L Datasheet.

### Software Development Kit (SDK)
An open source SDK is provided by SLAMTEC for developers to integrate an RPLIDAR into their system. The SDK inplements the RPLIDAR S2L communication protocol and provides a set of APIs for developers to use. The SDK is available on GitHub at the following link: <a href="https://github.com/slamtec/rplidar_sdk" target="_blank">RPLIDAR SDK</a> The SDK is compatible with Windows, Linux, and macOS operating systems. For more information about the SDK, please refer to the official SLAMTEC documentation.

## Protocol Basics
### Basic Communication Mode
To communicate with the RPLIDAR a non-textual binary data packet based protocol is used with all host systems. The data packets that are transmitted on the interface channel share a uniform format. The RPLIDAR will not send any data unless it receives a command from the host system. Data packets are broken down into two types: Request Packets and Response Packets. For instance, to get the RPLIDAR to start scanning and return scan data, a pre-defined Start Scan request packet must be sent to the device. 

There are three different request/response modes based on the related request types:
1. Request/Response Modes
    - The host system sends a request packet to the RPLIDAR. The RPLIDAR performs some action, and replies a response packet to the host system. Then, the RPLIDAR will standby for the next request packet. 
2. Single Request-Multiple Response Modes
    - In this mode, the host system sends a request packet to the RPLIDAR, and the RPLIDAR will constinously take measurements. Once a sample is retrieved, the results are sent back to the host system as individual response packets. The RPLIDAR will continue to take measurements and send back results until the host system sends a stop command.
3. Single Request-No Response
    - These types of request packets are used to control the RPLIDAR's operation. Request packets such as STOP, RESET Core, etc. are used to control the RPLIDAR's operation. The host system should wait for a period of time after sending these types of request packets to allow the RPLIDAR to complete the requested operation. The host system should not send any other request packets until the RPLIDAR has completed the requested operation. Otherwise, the request will be discarded by the RPLIDAR's protocol stack. 

### Request Packet Format
The request packet format is defined as follows:
| Start Flag | Command | Payload Size | Payload Data | Checksum |
|:-----------|:--------|:-------------|:-------------|:---------|
| 1 byte     | 1 byte  | 1 bytes      | 0-255 bytes  | 1 byte  |

The Start Flag is a fixed value of 0xA5 for each request packet. The RPLIDAR uses the Start Flag to identify the start of a new request packet. The Command is a 8bit (1 byte) value that defines the type of request that is being sent out, and it must follow the Start Flag. 

If the request packet contains a payload, the Payload Size field of size 1 byte is used to indicate the size of the payload data. Following the Payload Data field is the Checksum field calculated from the previous sent data. The Checksum value can be calculated performing a bitwise XOR operation by using the following formula:

$$checksum = 0 \oplus 0xA5 \oplus CmdType \oplus PayloadSize \oplus \sum_{i=0}^{n} Payload[i]$$

Where: 
- CmdType is the command type of the request packet
- PayloadSize is the size of the payload data
- Payload[i] is the ith byte of the payload data

__example:__ If the request packet is a Start Scan command, the request packet will be as follows:
| Start Flag | Command | Payload Size | Payload Data | Checksum |
|:-----------|:--------|:-------------|:-------------|:---------|
| 0xA5      | 0x20    | 0x00      | -           | 0x85     |

Note: That there is timing consideration when sending request packets. ALl bytes within a request packet must be sent within 5 seconnds. If the request packet is not sent within 5 seconds, the RPLIDAR will discard the request packet and wait for a new request packet.

### Response Packet Format
There are two types of response packets: __response descriptors__ and __data responses__. If the request requires a response, the RPLIDAR will send a response descriptor packet first, and then send the data response packet based on the request type. Only one response descriptor packet will be sent for each request/response transaction. The response descriptor packet is used to indicate the type of data response that will be sent by the RPLIDAR. The data response packet contains the actual data that is requested by the host system, and they all share a uniform format. The data response packet format is defined as follows:
| Start Flag1 | Start Flag2 | Data Response Length | Send Mode | Data Type |
|:------------|:------------|:--------------------|:----------|:----------|
| 1 byte (0xA5) | 1 byte (0x5A) | 30 bits | 2 bits | 1 byte |

A response descriptor has a fixed two bytes' pattern 0xA5 0x5A. This pattern is used to identify the start of a response descriptor packet. The Data Response Length field records the size of a single incoming data response packet in bytes. Note that all incoming data response packets within the transaction should have the same format and size. The Send Mode field indicates the request/response mode of the current transaction. 

|Send Mode| Description|
|:--------|:-----------|
| 0x0     |Single Request - Response Mode: The RPLIDAR will send a single data response packet to the host system after receiving a request packet.|
| 0x1     |Single Request - Multiple Response Mode: The RPLIDAR will continuously send data response packets to the host system after receiving a request packet. The RPLIDAR will continue to send data response packets until it receives a stop command from the host system.|
| 0x2     |Reserved: This mode is reserved for future use. The RPLIDAR will not send any data response packets to the host system after receiving a request packet.|
| 0x3     |Reserved: This mode is reserved for future use. The RPLIDAR will not send any data response packets to the host system after receiving a request packet.|

The Data Type describes the type of incoming data response packet. The type of data response is determined by the host's request packet. Host systems can choose different types of receiving data and handle the data response packets accordingly. 

## Request and Response Data
---
### Request Overview
| Request Name | Value | Payload | Response Mode | RPLIDAR Operation | Firmware Version |
|:-------------|:------|:--------|:--------------|:-----------------|:----------------|
| STOP | 0x25 | None | Single Request-No Response | Stop the RPLIDAR's current operation and return to idle state | All |
| RESET | 0x40 | None | Single Request-No Response | Reset the RPLIDAR's core system and return to idle state | all | 
| SCAN | 0x20 | None | Single Request-Multiple Response | Start the RPLIDAR's scanning operation and return scan data to the host system | all |
| EXPRESS_SCAN | 0x82 | Yes | Multiple response | Enter the scanning state and operate in high-speed sampling mode. | 1.17 | 
| FORCE_SCAN | 0x21 | None | Single Request-Multiple Response | Start the RPLIDAR's scanning operation and return scan data to the host system. The RPLIDAR will continue to scan even if the host system does not send a stop command. | all |
| GET_INFO | 0x50 | None | Single Request-Response | Get the RPLIDAR's device information. | all |
|GET_HEALTH | 0x52 | None | Single Request-Response | Get the RPLIDAR's device health status. | all |
|GET_SAMPLERATE | 0x59 | None | Single Request-Response | Get the RPLIDAR's current sampling rate. | all |
|GET_LIDAR_CONF | 0x84 | None | Single Request-Response | Get the RPLIDAR's configuration information. | 1.24 |

