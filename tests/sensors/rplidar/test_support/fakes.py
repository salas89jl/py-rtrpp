from collections import deque
from dataclasses import dataclass, field

from rtrpp.sensors.rplidar.exceptions import (
    TransportConnectionError,
)


@dataclass
class FakeTransport:
    responses: deque[bytes] = field(default_factory=deque)

    is_open: bool = False
    written: bytearray = field(default_factory=bytearray)
    internal_buffer: bytearray = field(default_factory=bytearray)

    fail_open: Exception | None = None
    fail_close: Exception | None = None
    fail_write: Exception | None = None
    fail_read: Exception | None = None
    fail_flush: Exception | None = None
    fail_reset_input: Exception | None = None
    fail_reset_output: Exception | None = None

    open_count: int = 0
    close_count: int = 0
    flush_count: int = 0
    reset_input_count: int = 0
    reset_output_count: int = 0

    def open(self) -> None:
        self.open_count += 1

        if self.fail_open is not None:
            raise self.fail_open

        self.is_open = True

    def close(self) -> None:
        self.close_count += 1

        if self.fail_close is not None:
            raise self.fail_close

        self.is_open = False

    def write(self, data: bytes) -> bytes:
        if not self.is_open:
            raise TransportConnectionError("Transport is not open.")

        if self.fail_write is not None:
            raise self.fail_write

        self.written.extend(data)
        return len(data)

    def read(self, size: int) -> bytes:
        if not self.is_open:
            raise TransportConnectionError("Transport is not open.")

        if self.fail_read is not None:
            raise self.fail_read

        if not self.responses:
            return b""

        responses = self.responses.popleft()
        return responses[:size]

    def flush(self) -> None:
        self.flush_count += 1

        if self.fail_flush is not None:
            raise self.fail_flush

    def reset_input_buffer(self) -> None:
        self.reset_input_count += 1

        if self.fail_reset_input is not None:
            raise self.fail_reset_input

    def reset_output_buffer(self) -> None:
        self.reset_output_count += 1

        if self.fail_reset_output is not None:
            raise self.fail_reset_output

    def reset_io_buffers(self) -> None:
        self.reset_input_buffer()
        self.reset_output_buffer()

    def clear_internal_buffer(self) -> None:
        self.internal_buffer.clear()


def queue_get_health_response(
    transport: FakeTransport,
    *,
    status: int = 0,
    error_code: int = 0,
) -> None:
    descriptor = b"\xa5\x5a\x03\x00\x00\x00\x06"
    payload = bytes([status, error_code & 0xFF, (error_code >> 8) & 0xFF])

    transport.responses.extend([descriptor, payload])


def queue_get_info_response(
    transport: FakeTransport,
    *,
    model: int = 0,
    firmware_version_minor: int = 0,
    firmware_version_major: int = 0,
    hardware_version: int = 0,
    serial_number: bytes | None = None,
) -> None:
    descriptor = b"\xa5\x5a\x14\x00\x00\x00\x04"
    payload = bytes([model, firmware_version_minor, firmware_version_major, hardware_version])

    if serial_number is not None:
        payload += serial_number
    else:
        payload += bytes([*range(16)])

    transport.responses.extend([descriptor, payload])


def queue_response_descriptor(
    transport: FakeTransport, *, response_descriptor: bytes = b""
) -> None:

    transport.responses.extend([response_descriptor])


def queue_single_scan_data_response(
    transport: FakeTransport,
    *,
    start_flag: bytes = b"\x01",
    quality: int = 0,
    checkbit: int = 0x01,
    angle_degrees: float = 90.0,
    distance_mm: float = 1000.0,
) -> None:
    first_byte = ((quality & 0xFF) << 2) | (start_flag[0] & 0x03)

    angle_raw = int(angle_degrees * 64) 
    # angle_bytes = angle_raw.to_bytes(2, "little")

    b1, b2 = angle_raw.to_bytes(2, "little")

    angle_bytes = (((b2 << 8) | b1) << 1).to_bytes(2, "little")
   

    # split angle_bytes into two bytes and set the checkbit in the second byte
    angle_bytes_with_checkbit = bytes([(angle_bytes[0] << 1) | (checkbit & 0x01), angle_bytes[1]])

    distance_raw = int(distance_mm * 4) & 0xFFFF
    distance_bytes = distance_raw.to_bytes(2, "little")

    payload = bytes([first_byte]) + angle_bytes_with_checkbit + distance_bytes

    transport.responses.append(payload)

def queue_multiple_scan_data_responses(
    transport: FakeTransport,
    *,
    num_responses: int = 5,
    _start_flag: bytes = b"\x01",
    angle_increment: float = 10.0,
    distance_mm: float = 10.0,
):

    for i in range(num_responses):
        print(i)
        angle_degrees = angle_increment * i
        current_distance_mm = distance_mm * i

        if angle_degrees > 360: 
            break

        queue_single_scan_data_response(
            transport,
            start_flag= _start_flag if i == 0 else b"\x02",
            quality=41,
            checkbit=0x01,
            angle_degrees=angle_degrees,
            distance_mm=current_distance_mm,
        )

    if _start_flag == b"\x01":
        queue_single_scan_data_response(
            transport,
            start_flag=b"\x01",
            quality=41,
            checkbit=0x01,
            angle_degrees=0.00,
            distance_mm=0.00,
        )