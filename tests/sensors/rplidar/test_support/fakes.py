from collections import deque
from dataclasses import dataclass, field

from rtrpp.sensors.rplidar.exceptions import (
    TransportTimeoutError,
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
