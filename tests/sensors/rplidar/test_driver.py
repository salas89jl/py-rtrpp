import pytest
import serial

from rtrpp.sensors.rplidar.driver import RPLidarDriver
from rtrpp.sensors.rplidar.protocol import RPLidarCommand
from rtrpp.sensors.rplidar.exceptions import (
    RPLidarConnectionError,
    RPLidarProtocolError,
    RPLidarTimeoutError,
    RPLidarDeviceError
)
class MockTransport:
    """ A mock transport class that simulates the behavior of the RPLidarTransport class for testing purposes. """
    def __init__(
            self,
            responses: list[bytes] | None = None,
            fail_on_write: bool = False, 
            fail_on_read: bool = False,
    ):
        self.responses = list(responses or [])
        self.fail_on_write = fail_on_write
        self.fail_on_read = fail_on_read
        self.written = b""

    def write(self, data) -> int:
        if self.fail_on_write:
            raise serial.SerialException("Simulated write failure.")
        
        self.written += data
        return len(data)
    
    def read(self, size: int) -> bytes:
        if self.fail_on_read:
            raise serial.SerialException("Simulated read failure.")
        
        if not self.responses:
            return b""
        
        response = self.responses.pop(0)
        return response[:size]

class OSErrorTransport:
    def __init__(
            self,
            fail_on_write: bool = False,
            fail_on_read: bool = False,
    ):
        self.fail_on_write = fail_on_write
        self.fail_on_read = fail_on_read

    def write(self, data: bytes) -> int:
        if self.fail_on_write:
            raise OSError("Simulated device disconnection.")
    
    def read(self, size: int) -> bytes:
        if self.fail_on_read:
            raise OSError("Simulated device disconnection.")
    

def create_test_driver(response_descriptor, data_response):
    """ Creates a test driver with a mock transport that returns the specified descriptor and data responses."""
    responses = [response_descriptor,data_response]
    transport = MockTransport(responses)
    return RPLidarDriver(transport)


# Tests for driver get_info() helper function
def test_get_info_with_valid_request_and_response():

    response_descriptor = b"\xA5\x5A\x14\x00\x00\x00\x04"
    data_response = bytes([0x01,0x05,0x02,0x10, *range(16)])
    responses = [response_descriptor,data_response]

    transport = MockTransport(responses)
    driver = RPLidarDriver(transport)

    info = driver.get_info()

    assert driver._transport.written == bytes([
        0xA5,
        RPLidarCommand.GET_INFO.value
    ])
    assert info.model == 1
    assert info.firmware_version_minor == 5
    assert info.firmware_version_major == 2
    assert info.hardware_version == 16
    assert info.serial_number == bytes(range(16))

def test_get_info_reads_invalid_start_flags():
    descriptor = b"\x00\x00\x14\x00\x00\x00\x04"
    data_response = bytes([0x01,0x05,0x02,0x10, *range(16)])

    driver = create_test_driver(descriptor, data_response)

    with pytest.raises(RPLidarProtocolError) as exc_info:
        driver.get_info()

    assert isinstance(exc_info.value.__cause__, ValueError)

def test_get_info_with_invalid_response_descriptor_length():
    # Size of data length is 21 bytes from bytes(0x15,0x00,0x00)
    response_descriptor = b"\xA5\x5A\x15\x00\x00\x00\x04" 
    data_response = bytes([0x01,0x05,0x02,0x10, *range(16)])

    driver = create_test_driver(response_descriptor, data_response)

    with pytest.raises(RPLidarProtocolError):
        driver.get_info()

def test_get_info_with_invalid_descriptor_send_mode():

    response_descriptor = b"\xA5\x5A\x14\x00\x00\x40\x04" 
    data_response = bytes([0x01,0x05,0x02,0x10, *range(16)])

    driver = create_test_driver(response_descriptor, data_response)

    with pytest.raises(RPLidarProtocolError):
        driver.get_info()

def test_get_info_with_invalid_descriptor_data_type():

    # GET_INFO expectes 0x04 but receives 0x05
    response_descriptor = b"\xA5\x5A\x14\x00\x00\x00\x05" 
    data_response = bytes([0x01,0x05,0x02,0x10, *range(16)])

    driver = create_test_driver(response_descriptor, data_response)

    with pytest.raises(RPLidarProtocolError):
        driver.get_info()

def test_get_info_preserves_binary_serial_number():

    response_descriptor = b"\xA5\x5A\x14\x00\x00\x00\x04"
    serial_number = bytes([
        0xFF, 0x80, 0x7A, 0x00,
        0x4B, 0x34, 0x28, 0xA2, 
        0x8A, 0x2F, 0x8E, 0x9F,
        0x3A, 0x00, 0x24, 0x67
    ])

    data_response = bytes([0x01, 0x05, 0x02, 0x10]) + serial_number

    driver = create_test_driver(response_descriptor, data_response)

    info = driver.get_info()

    assert info.serial_number == serial_number

def test_get_info_timeout_while_reading_descriptor():
    mock_transport = MockTransport(
        responses=[
            b"\xA5\x5A\x14", # Only 3 of the expected 7 bytes
        ]
    )

    driver = RPLidarDriver(mock_transport)

    with pytest.raises(
        RPLidarTimeoutError,
        match=r"GET_INFO descriptor expected 7 bytes but received 3 bytes"
    ):
        driver.get_info()

def test_get_info_timeout_while_reading_data():
    response_descriptor = b"\xA5\x5A\x14\x00\x00\x00\x04"
    partial_data = bytes([
        0x01, # model
        0x05, # firmware minor
        0x02  # firmware major
    ])

    driver = create_test_driver(
        response_descriptor=response_descriptor,
        data_response=partial_data
    )

    with pytest.raises(
        RPLidarTimeoutError, 
        match=r"GET_INFO expected 20 bytes but received 3 bytes"
    ):
        driver.get_info()

def test_get_info_connection_error_during_write():
    transport = MockTransport(fail_on_write=True)
    driver = RPLidarDriver(transport)

    with pytest.raises(RPLidarConnectionError) as exc_info:
        driver.get_info()

    assert isinstance(exc_info.value.__cause__, serial.SerialException)

def test_get_info_connection_error_during_read():
    transport = MockTransport(fail_on_read=True)
    driver = RPLidarDriver(transport)

    with pytest.raises(RPLidarConnectionError) as exc_info:
        driver.get_info()

    assert isinstance(exc_info.value.__cause__, serial.SerialException)

def test_get_info_connection_oserror_during_write():
    transport = OSErrorTransport(fail_on_write=True)
    driver = RPLidarDriver(transport)

    with pytest.raises(RPLidarConnectionError) as exc_info:
        driver.get_info()

    assert isinstance(exc_info.value.__cause__, OSError)

def test_get_info_connection_oserror_during_read():
    transport = OSErrorTransport(fail_on_read=True)
    driver = RPLidarDriver(transport)

    with pytest.raises(RPLidarConnectionError) as exc_info:
        driver.get_info()

    assert isinstance(exc_info.value.__cause__, OSError)

# Tests for driver get_health() helper function
def test_get_health_with_valid_request_and_response():
    response_descriptor = b"\xA5\x5A\x03\x00\x00\x00\x06"
    data_response = b"\x00\x01\x00"

    driver = create_test_driver(
        response_descriptor=response_descriptor,
        data_response=data_response
    )

    health = driver.get_health()

    assert driver._transport.written == bytes([
        0xA5,
        RPLidarCommand.GET_HEALTH.value
    ])
    assert health.status == 0
    assert health.error_code == 1



def test_get_health_with_invalid_descriptor_size():
    response_descriptor = b"\xA5\x5A\x03"
    data_response = b"\x00\x01\x00"

    driver = create_test_driver(
        response_descriptor=response_descriptor,
        data_response=data_response
    )

    with pytest.raises(RPLidarTimeoutError):
        driver.get_health()

def test_get_health_with_invalid_descriptor_send_mode():
    response_descriptor = b"\xA5\x5A\x03\x00\x00\x80\x06" # Send mode received is 2
    data_response = b"\x00\x01\x00"

    driver = create_test_driver(
        response_descriptor=response_descriptor,
        data_response=data_response
    )

    with pytest.raises(RPLidarProtocolError):
        driver.get_health()

def test_get_health_with_invalid_descriptor_data_type():
    response_descriptor = b"\xA5\x5A\x03\x00\x00\x00\x05" # GET_HEALTH expects 0x06 but receives 0x05
    data_response = b"\x00\x01\x00"

    driver = create_test_driver(
        response_descriptor=response_descriptor,
        data_response=data_response
    )

    with pytest.raises(RPLidarProtocolError):
        driver.get_health()

def test_get_health_timeout_while_reading_descriptor():
    mock_transport = MockTransport(
        responses=[
            b"\xA5\x5A\x03",
        ]
    )

    driver = RPLidarDriver(mock_transport)

    with pytest.raises(
        RPLidarTimeoutError,
        match=r"GET_HEALTH descriptor expected 7 bytes but received 3 bytes"
    ):
        driver.get_health()

def test_get_health_timeout_while_reading_data():
    response_descriptor = b"\xA5\x5A\x03\x00\x00\x00\x06"
    partial_data = b"\x01\x02"

    driver = create_test_driver(
        response_descriptor=response_descriptor,
        data_response=partial_data
    )

    with pytest.raises(
        RPLidarTimeoutError,
        match=r"GET_HEALTH expected 3 bytes but received 2 bytes"
    ):
        driver.get_health()
def test_get_health_returns_warning_status():
    response_descriptor = b"\xA5\x5A\x03\x00\x00\x00\x06"
    data_response = b"\x01\x34\x12"

    driver = create_test_driver(
        response_descriptor=response_descriptor,
        data_response=data_response
    )

    health = driver.get_health()

    assert health.status == 1
    assert health.error_code == 0x1234
    
def test_get_health_reads_raises_error_status():
    response_descriptor = b"\xA5\x5A\x03\x00\x00\x00\x06"
    data_response = b"\x02\x34\x12"

    driver = create_test_driver(
        response_descriptor=response_descriptor,
        data_response=data_response
    )

    with pytest.raises(
        RPLidarDeviceError,
        match=r"RPLIDAR reported an internal error: 0x1234"
    ):
        driver.get_health()

def test_get_health_connection_error_during_write():
    transport = MockTransport(fail_on_write=True)
    driver = RPLidarDriver(transport)

    with pytest.raises(RPLidarConnectionError) as exc_info:
        driver.get_health()

    assert isinstance(exc_info.value.__cause__, serial.SerialException)

def test_get_health_connection_error_during_read():
    transport = MockTransport(fail_on_read=True)
    driver = RPLidarDriver(transport)

    with pytest.raises(RPLidarConnectionError) as exc_info:
        driver.get_health()

    assert isinstance(exc_info.value.__cause__, serial.SerialException)

def test_get_health_connection_oserror_during_write():
    transport = OSErrorTransport(fail_on_write=True)
    driver = RPLidarDriver(transport)

    with pytest.raises(RPLidarConnectionError) as exc_info:
        driver.get_health()

    assert isinstance(exc_info.value.__cause__, OSError)

def test_get_health_connection_oserror_during_read():
    transport = OSErrorTransport(fail_on_read=True)
    driver = RPLidarDriver(transport)

    with pytest.raises(RPLidarConnectionError) as exc_info:
        driver.get_health()

    assert isinstance(exc_info.value.__cause__, OSError)

# Tests for driver get_samplerate() helper function
def test_get_samplerate_with_valid_request_and_response():
    response_descriptor = b"\xA5\x5A\x04\x00\x00\x00\x15"
    data_response = b"\x01\x02\x34\x12"

    driver = create_test_driver(
        response_descriptor=response_descriptor,
        data_response=data_response
    )

    samplerate = driver.get_samplerate()

    assert driver._transport.written == bytes([
        0xA5,
        RPLidarCommand.GET_SAMPLERATE.value
    ])
    assert samplerate.t_standard == 0x0201
    assert samplerate.t_express == 0x1234

def test_get_samplerate_with_invalid_descriptor_size():
    response_descriptor = b"\xA5\x5A\x04" # expects 7 bytes
    data_response = b"\x00\x01\x00\x00"
    
    driver = create_test_driver(
        response_descriptor=response_descriptor,
        data_response=data_response
    )

    with pytest.raises(RPLidarTimeoutError):
        driver.get_samplerate()

def test_get_samplerate_with_invalid_descriptor_send_mode():
    response_descriptor = b"\xA5\x5A\x04\x00\x00\x40\x15" # Expects 0, receives 2.
    data_response = b"\x00\x01\x00\x00"

    driver = create_test_driver(
        response_descriptor=response_descriptor,
        data_response=data_response
    )

    with pytest.raises(RPLidarProtocolError):
        driver.get_samplerate()

def test_get_samplerate_with_invalid_descripor_data_type():
    response_descriptor = b"\xA5\x5A\x04\x00\x00\x00\x80" # Expects 0x15, but receives 0x80
    data_response = b"\x00\x01\x12\x34"

    driver = create_test_driver(
        response_descriptor=response_descriptor,
        data_response=data_response
    )

    with pytest.raises(RPLidarProtocolError):
        driver.get_samplerate()

def test_get_samplerate_timeout_while_reading_descriptor():
    mock_transport = MockTransport(
        responses=[
            b"\xA5\x5A\x04",
        ]
    )

    driver = RPLidarDriver(mock_transport)
    
    with pytest.raises(
        RPLidarTimeoutError,
        match=r"GET_SAMPLERATE descriptor expected 7 bytes but received 3 bytes"
    ):
        driver.get_samplerate()

def test_get_samplerate_timeout_while_reading_data():
    response_descriptor = b"\xA5\x5A\x04\x00\x00\x00\x15"
    partial_data = b"\x12\x02"

    driver = create_test_driver(
        response_descriptor=response_descriptor,
        data_response=partial_data
    )

    with pytest.raises(
        RPLidarTimeoutError,
        match=r"GET_SAMPLERATE expected 4 bytes but received 2 bytes"
    ):
        driver.get_samplerate()

def test_get_samplerate_connection_error_during_write():
    transport = MockTransport(fail_on_write=True)
    driver = RPLidarDriver(transport)

    with pytest.raises(RPLidarConnectionError) as exc_info:
        driver.get_samplerate()

    assert isinstance(exc_info.value.__cause__, serial.SerialException)

def test_get_samplerate_connection_error_during_read():
    transport = MockTransport(fail_on_read=True)
    driver = RPLidarDriver(transport)

    with pytest.raises(RPLidarConnectionError) as exc_info:
        driver.get_samplerate()

    assert isinstance(exc_info.value.__cause__, serial.SerialException)

def test_get_samplerate_connection_oserror_during_write():
    transport = OSErrorTransport(fail_on_write=True)
    driver = RPLidarDriver(transport)

    with pytest.raises(RPLidarConnectionError) as exc_info:
        driver.get_samplerate()

    assert isinstance(exc_info.value.__cause__, OSError)

def test_get_samplerate_connection_oserror_during_read():
    transport = OSErrorTransport(fail_on_read=True)
    driver = RPLidarDriver(transport)

    with pytest.raises(RPLidarConnectionError) as exc_info:
        driver.get_samplerate()

    assert isinstance(exc_info.value.__cause__, OSError)

# Tests for stop helper function
def test_stop_valid_write():
    transport = MockTransport()
    driver = RPLidarDriver(transport)

    driver.stop()

    assert driver._transport.written == bytes([
        0xA5,
        RPLidarCommand.STOP.value
    ])

def test_stop_connection_error_during_write():
    transport = MockTransport(fail_on_write=True)
    driver = RPLidarDriver(transport)

    with pytest.raises(RPLidarConnectionError) as exc_info:
        driver.stop()
    
    assert isinstance(exc_info.value.__cause__, serial.SerialException)

def test_stop_connection_oserror_during_write():
    transport = OSErrorTransport(fail_on_write=True)
    driver = RPLidarDriver(transport)

    with pytest.raises(RPLidarConnectionError) as exc_info:
        driver.stop()

    assert isinstance(exc_info.value.__cause__, OSError)

# Tests for reset helper function

def test_reset_valid_write():
    transport = MockTransport()
    driver = RPLidarDriver(transport)

    driver.reset()

    assert driver._transport.written == bytes([
        0xA5,
        RPLidarCommand.RESET.value
    ])

def test_reset_connection_error_during_write():
    transport = MockTransport(fail_on_write=True)
    driver = RPLidarDriver(transport)

    with pytest.raises(RPLidarConnectionError) as exc_info:
        driver.reset()
    
    assert isinstance(exc_info.value.__cause__, serial.SerialException)

def test_reset_connection_oserror_during_write():
    transport = OSErrorTransport(fail_on_write=True)
    driver = RPLidarDriver(transport)

    with pytest.raises(RPLidarConnectionError) as exc_info:
        driver.reset()

    assert isinstance(exc_info.value.__cause__, OSError)