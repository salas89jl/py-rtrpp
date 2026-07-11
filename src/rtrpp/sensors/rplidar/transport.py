from typing import Optional
import serial


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

    def open(self) -> "RPLidarTransport":
        """
        Opens the serial connection to the RPLidar device.
        """

        self.serial_connection = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout
        )
        return self

    def close(self) -> None:
        """
        Closes the serial connection to the RPLidar device.
        """
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()

    def read(self, size: int) -> bytes:
        """
        Reads a specified number of bytes from the RPLidar device.

        :param size: The number of bytes to read.
        :return: The bytes read from the device.
        """
        
        return self.serial_connection.read(size)

    def write(self, data: bytes) -> bytes:
        """ Writes data to the RPLidar device. """
        if not self.is_open:
            raise RuntimeError("Serial connection is not open.")
        
        return self.serial_connection.write(data)

    def reset_input_buffer(self):
        """ Resets the input buffer of the serial connection. """
        if self.is_open:
            self.serial_connection.reset_input_buffer()

    def reset_output_buffer(self):
        """ Resets the output buffer of the serial connection. """
     
        if self.is_open:
            self.serial_connection.reset_output_buffer()
    
    def reset_buffers(self):
        """ Resets both the input and output buffers of the serial connection. """
        self.reset_input_buffer()
        self.reset_output_buffer()
        
    @property
    def is_open(self) -> bool:
        """ Return True if the serial connection is open. """
        return (
            self.serial_connection is not None
            and self.serial_connection.is_open
        )