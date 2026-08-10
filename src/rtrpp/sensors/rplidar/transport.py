from typing import Optional

import serial

from .exceptions import (
    TransportConnectionError,
    TransportTimeoutError,
)

# RPLidarTransport is responsible for low-level serial communication:
# opening/closing the port, reading/writing raw bytes, and resetting buffers.
# It does not know about RPLIDAR commands, responses, packets, or scan data.


class RPLidarTransport:
    def __init__(self, port: str, baudrate: int = 1_000_000, timeout: float = 5.0):
        """
        Initializes the RPLidarTransport class with the specified serial port and baudrate.

        :param port: The serial port to which the RPLidar device is connected.
        :param baudrate: The baudrate for the serial connection (default is 1_000_000).
        :param timeout: The timeout for serial read operations in seconds (default is 5.0).
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout  # Timeout for serial read operations in seconds
        self.serial_connection: Optional[serial.Serial] = None
        self._internal_buffer: bytearray = bytearray()

    # Serial connection management methods
    def open(self) -> "RPLidarTransport":
        """Opens the serial connection to the RPLidar device."""
        try:
            connection = self.serial_connection = serial.Serial(
                port=self.port, baudrate=self.baudrate, timeout=self.timeout
            )
        except (serial.SerialException, OSError) as exc:
            self.serial_connection = None
            raise TransportConnectionError(f"Failed to open serial connection. {exc}") from exc

        self.serial_connection = connection
        return self

    def close(self) -> None:
        """Closes the serial connection to the RPLidar device."""

        connection = self.serial_connection

        if connection is None:
            return

        if not connection.is_open:
            self.serial_connection = None
            return
        try:
            connection.close()

        except (serial.SerialException, OSError) as exc:
            raise TransportConnectionError(f"Serial connection failed to close. {exc}") from exc

        self.serial_connection = None

    def read(self, size: int) -> bytes:
        """
        Reads a specified number of bytes from the RPLidar device.

        :param size: The number of bytes to read.
        :return: The bytes read from the device.
        """

        if size <= 0:
            raise ValueError("size must be greater than zero")

        if not self.is_open:
            raise TransportConnectionError("Cannot read the serial port is not open")

        buffer = bytearray()

        while len(buffer) < size:
            try:
                remaining = size - len(buffer)
                chunk = self.serial_connection.read(remaining)

            except serial.SerialException as exc:
                raise TransportConnectionError(f"Serial read failed. {exc}") from exc
            except OSError as exc:
                raise TransportConnectionError(
                    f"Operating-system error during serial read. {exc}"
                ) from exc

            if not chunk:
                raise TransportTimeoutError(
                    f"Timed out after receving {len(buffer)} of {size} bytes"
                )

            buffer.extend(chunk)

        return bytes(buffer)

    def write(self, data: bytes) -> bytes:
        """Writes data to the RPLidar device."""

        if not self.is_open:
            raise TransportConnectionError("Serial connection is not open.")

        try:
            self.serial_connection.write(data)

        except serial.SerialException as exc:
            raise TransportConnectionError(
                f"Error: Error communicating with serial port: {exc}"
            ) from exc

        except serial.SerialTimeoutException as exc:
            raise TransportTimeoutError(
                f"Error: Transport's write command timed out. {exc}"
            ) from exc

    # Serial buffer management methods
    def flush(self) -> None:
        """Waits for the output data buffer to be transmitted."""

        if not self.is_open:
            raise TransportConnectionError("Serial connection is not open.")

        try:
            self.serial_connection.flush()

        except serial.SerialException as exc:
            raise TransportConnectionError(f"Serial flush failed. {exc}") from exc

        except OSError as exc:
            raise TransportConnectionError(
                f"Operating-system error during serial connection flush. {exc}"
            ) from exc

    def reset_input_buffer(self) -> None:
        """Resets the input buffer of the serial connection."""

        if not self.is_open:
            raise TransportConnectionError("Serial connection is not open.")

        try:
            self.serial_connection.reset_input_buffer()

        except serial.SerialException as exc:
            raise TransportConnectionError(
                f"Failed to reset serial connections input data buffer. {exc}"
            ) from exc

        except OSError as exc:
            raise TransportConnectionError(
                f"Operating-system error during serial connection's input data buffer. {exc}"
            )

    def reset_output_buffer(self) -> None:
        """Resets the output buffer of the serial connection."""

        if not self.is_open:
            raise TransportConnectionError("Serial connection is not open.")

        try:
            self.serial_connection.reset_output_buffer()

        except serial.SerialException as exc:
            raise TransportConnectionError(
                f"Failed to reset serial connections output data buffer. {exc}"
            ) from exc

        except OSError as exc:
            raise TransportConnectionError(
                f"Operating-system error during serial connection's output data buffer. {exc}"
            )

    def reset_io_buffers(self) -> None:
        """Resets both the input and output buffers of the serial connection."""
        self.reset_input_buffer()
        self.reset_output_buffer()

    @property
    def is_open(self) -> bool:
        """Return True if the serial connection is open."""
        return self.serial_connection is not None and self.serial_connection.is_open

    # Internal buffer management properties
    def clear_internal_buffer(self) -> None:
        """Clears the internal buffer used for reading data."""
        self._internal_buffer.clear()

    @property
    def internal_buffer_size(self) -> int:
        """Returns the size of the internal buffer used for reading data."""
        return len(self._internal_buffer)

    @property
    def internal_buffer(self) -> bytes:
        """Returns a copy of the internal buffer used for reading data."""
        return bytes(self._internal_buffer)
