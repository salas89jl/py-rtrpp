from dataclasses import dataclass
from enum import Enum

SYNC_BYTE = 0xA5
SYNC_BYTE_RESPONSE = 0x5A


class RPLidarCommand(Enum):
    """Named command values for RPLIDAR commands."""

    STOP = 0x25
    RESET = 0x40
    SCAN = 0x20
    EXPRESS_SCAN = 0x82
    FORCE_SCAN = 0x21
    GET_INFO = 0x50
    GET_HEALTH = 0x52
    GET_SAMPLERATE = 0x59
    GET_LIDAR_CONF = 0x84


# Time specifications for RPLIDAR requests.
POST_COMMAND_DELAYS = {RPLidarCommand.STOP: 0.001, RPLidarCommand.RESET: 0.002}


class RPLidarScanningMode(Enum):
    """Scanning modes for RPLIDAR device."""

    STANDARD = "Standard Mode"
    DENSE = "Dense Mode"
    SENSITIVITY = "Sensitivity Mode"
    STABILITY = "Stability Mode"
    STAND_BY = "Stand By"
    INACTIVE = "Inactive"


class RPLidarWorkingState(Enum):
    """Major Working States of RPLIDAR device."""

    IDLE = "Idle"
    SCANNING = "Scanning"
    PROTECTION_STOP = "Protection Stop"
    NOT_CONNECTED = "Not Connected"


class RPLidarResponseType(Enum):
    """Response Descriptor Data Type List."""

    # Scanning Data Types
    MEASUREMENT_DATA = 0x81
    EXPRESS_MEASUREMENT_DATA = 0x82
    EXTENDED_MEASUREMENT_DATA = 0x84
    DENSE_MEASUREMENT_DATA = 0x85

    # Info & Health Types
    DEVICE_INFO = 0x04
    DEVICE_HEALTH = 0x06
    DEVICE_SAMPLERATE = 0x15
    DEVICE_LIDAR_CONF = 0x20


class RPLidarSendMode(Enum):
    """Named send mode values for RPLIDAR responses."""

    SINGLE_RESPONSE = 0x0
    MULTIPLE_RESPONSE = 0x1


class RPLidarHealthStatus(Enum):
    """Named health status values for RPLIDAR device health."""

    GOOD = 0
    WARNING = 1
    ERROR = 2


class RPLidarDataLength(Enum):
    """Named data length values for RPLIDAR response packets."""

    # Scanning Data Lengths
    SCAN_DATA = 5
    EXPRESS_DATA = 84
    EXTENDED_DATA = 132
    DENSE_DATA = 84

    # Info & Health Data Lengths
    GET_INFO = 20
    GET_HEALTH = 3
    GET_SAMPLERATE = 4


@dataclass(frozen=True)
class RPLidarRequest:
    """Represents a command request packet that is converted to bytes to be sent to the RPLIDAR."""

    command: int
    payload: bytes | None = None

    def to_bytes(self) -> bytes:
        if self.payload:
            payload_size = len(self.payload)
            checksum = self.compute_checksum(self.command, payload_size, self.payload)
            return bytes([SYNC_BYTE, self.command, payload_size]) + self.payload + bytes([checksum])

        return bytes([SYNC_BYTE, self.command])

    @staticmethod
    def compute_checksum(command: int, payload_size: int, payload: bytes) -> int:
        checksum = 0 ^ SYNC_BYTE ^ command ^ payload_size
        for byte in payload:
            checksum ^= byte
        return checksum & 0xFF


@dataclass(frozen=True)
class RPLidarResponseDescriptor:
    """Represents a response descriptor packet parsed from bytes received from the RPLIDAR."""

    data_length: int
    send_mode: int
    data_type: int


@dataclass(frozen=True)
class RPLidarScanData:
    """Represents a scan data packet parsed from bytes received from RPLIDAR in SCAN mode."""

    start_flag: bool
    quality: int
    angle_degrees: float
    distance_mm: float


@dataclass(frozen=True)
class RPLidarGetInfoData:
    """Represents a response packet parsed from bytes received from RPLIDAR in GET_INFO mode."""

    model: int
    firmware_version_minor: int
    firmware_version_major: int
    hardware_version: int
    serial_number: bytes


@dataclass(frozen=True)
class RPLidarGetHealthData:
    """Represents a response packet parsed from bytes received from RPLIDAR in GET_HEALTH mode."""

    status: int
    error_code: int


@dataclass(frozen=True)
class RPLidarGetSamplerateData:
    """Represents a response packet parse from bytes received from  RPLIDAR in GET_HEALTH mode."""

    t_standard: int
    t_express: int


@dataclass(frozen=True)
class RPLidarGetLidarConfData:
    """Represents a response packet parse from bytes received from  RPLIDAR in GET_HEALTH mode."""

    config_type: int
    payload: bytes


@dataclass
class RPLidarScanningState:
    is_active: bool
    packet_size: int
    mode: RPLidarScanningMode | None
    response_type: RPLidarResponseType | None = None
    rpm: float | None = None
    completed_scan_count: int | None = None


# Helper functions
def build_request(command: RPLidarCommand, payload: bytes = b"") -> bytes:
    """Builds a request byte for the driver to send to the lidar device."""
    if not isinstance(command, RPLidarCommand):
        raise ValueError("Invalid command type. Must be an instance of RPLidarCommand.")

    if len(payload) > 255:
        raise ValueError("Invalid payload size. Must not exceed 255 bytes")

    return RPLidarRequest(command.value, payload).to_bytes()


def parse_response_descriptor(packet: bytes) -> RPLidarResponseDescriptor:
    """Parses a response descriptor packet from bytes received from the RPLIDAR device."""
    if len(packet) != 7:
        raise ValueError(
            f"Response descriptor must be exactly 7 bytes; received {len(packet)} bytes."
        )

    b0, b1, b2, b3, b4, b5, b6 = packet
    if b0 != SYNC_BYTE or b1 != SYNC_BYTE_RESPONSE:
        raise ValueError("Invalid response descriptor start flags. ")

    raw_length_mode = b2 | (b3 << 8) | (b4 << 16) | (b5 << 24)

    data_length = raw_length_mode & 0x3FFFFFFF  # Mask to get the lower 30 bits for data length
    
    send_mode = (raw_length_mode >> 30) & 0x03  # Mask to get the upper 2 bits for send mode

    data_type = b6


    return RPLidarResponseDescriptor(
        data_length=data_length, send_mode=send_mode, data_type=data_type
    )


def parse_scan_data(packet: bytes) -> RPLidarScanData:
    """Decodes raw scan data received from the RPLIDAR using SCAN request into structured format."""
    if len(packet) != 5:
        raise ValueError("SCAN data packet must be exactly 5 bytes.")

    b0, b1, b2, b3, b4 = packet

    start_flag = b0 & 0x01
    inverse_start_flag = (b0 >> 1) & 0x01

    if start_flag == inverse_start_flag:
        raise ValueError(
            f"Invalid: S Flag: {start_flag} !S Flag: {inverse_start_flag} in scan packet. "
        )

    if (b1 & 0x01) != 1:
        raise ValueError("Invalid check bit in scan measurement packet. ")

    quality = b0 >> 2
    angle_q6 = ((b2 << 8) | b1) >> 1
    distance_q2 = (b4 << 8) | b3

    return RPLidarScanData(
        quality=quality,
        angle_degrees=angle_q6 / 64.0,
        distance_mm=distance_q2 / 4.0,
        start_flag=bool(start_flag),
    )


def parse_get_info_response(packet: bytes) -> RPLidarGetInfoData:
    """Parse the 20-byte GET_INFO response packet."""

    if len(packet) != 20:
        raise ValueError("GET_INFO response packet must be exactly 20 bytes.")

    model = packet[0]
    firmware_version_minor = packet[1]
    firmware_version_major = packet[2]
    hardware_version = packet[3]
    serial_number = packet[4:20]

    return RPLidarGetInfoData(
        model=model,
        firmware_version_minor=firmware_version_minor,
        firmware_version_major=firmware_version_major,
        hardware_version=hardware_version,
        serial_number=serial_number,
    )


def parse_get_health_response(packet: bytes) -> RPLidarGetHealthData:
    """Parse the 3-byte GET_HEALTH response packet."""

    if len(packet) != 3:
        raise ValueError("GET_HEALTH response packet must be exactly 3 bytes. ")

    status = packet[0]

    if not any(item.value == status for item in RPLidarHealthStatus):
        raise ValueError(f"Invalid GET_HEALTH status: {status}")

    error_code = int.from_bytes(packet[1:3], byteorder="little")

    return RPLidarGetHealthData(status=status, error_code=error_code)


def parse_get_samplerate_response(packet: bytes) -> RPLidarGetSamplerateData:
    """Parse the raw GET_SAMPLERATE response data received from the RPLIDAR device."""

    if len(packet) != 4:
        raise ValueError("GET_SAMPLERATE response packet must be exactly 4 bytes. ")

    t_standard = int.from_bytes(packet[0:2], byteorder="little")

    t_express = int.from_bytes(packet[2:4], byteorder="little")

    return RPLidarGetSamplerateData(t_standard=t_standard, t_express=t_express)


# *** Under Construction ***
# GET_LIDAR_CONF returns completely different data structures
# depending on the type_id. This feature(s) will be implemented
# after implementation of driver layer.

# def parse_get_lidar_conf_response(packet: bytes) -> RPLidarGetLidarConfData:
#     """
# Parse the raw GET_LIDAR_CONF response data from the RPLIDAR device.
# Payload field size is defined by each specific configuration type
# """

#     if len(packet) < 4:
#         raise ValueError("GET_LIDAR_CONF response packet must be at least 4 bytes. ")

#     config_type = (
#         packet[0]
#         | (packet[1] << 8)
#         | (packet[2] << 16)
#         | (packet[3] << 24)
#     )

#     payload = packet[4:]

#     if len(payload) > 255:
#         raise ValueError("GET_LIDAR_CONF payload cannot exceed 255 bytes. ")

#     return RPLidarGetLidarConfData(
#         config_type=config_type,
#         payload=payload
#     )
