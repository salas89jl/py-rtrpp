# from unittest.mock import patch

# import pytest
# import serial

# from rtrpp.sensors.rplidar.driver import RPLidarDriver
# from rtrpp.sensors.rplidar.exceptions import (
#     RPLidarConnectionError,
#     RPLidarDeviceError,
#     RPLidarProtocolError,
#     RPLidarTimeoutError,
# )
# from rtrpp.sensors.rplidar.protocol import (
#     RPLidarCommand,
#     RPLidarDataLength,
#     RPLidarResponseType,
#     RPLidarScanningMode,
#     RPLidarWorkingState,
# )

# MOCK_GOOD_HEALTH_DESCRIPTOR = b"\xa5\x5a\x03\x00\x00\x00\x06"
# MOCK_GOOD_HEALTH_RESPONSE = b"\x00\x01\x00"
# class MockTransport:
#     """
#     A mock transport class that simulates the behavior of the
#     RPLidarTransport class for testing purposes.
#     """

#     def __init__(
#         self,
#         responses: list[bytes] | None = None,
#         fail_on_write: bool = False,
#         fail_on_read: bool = False,
#     ):
#         self.responses = list(responses or [])
#         self.fail_on_write = fail_on_write
#         self.fail_on_read = fail_on_read
#         self.written = bytearray()

#         self._is_open = False

#     def open(self) -> None:
#         self._is_open = True

#     def write(self, data:bytes) -> int:
#         if self.fail_on_write:
#             raise serial.SerialException("Simulated write failure.")

#         self.written.extend(data)
#         self.written.pop(0)
#         return len(self.written)

#     def read(self, size: int) -> bytes:
#         if self.fail_on_read:
#             raise serial.SerialException("Simulated read failure.")

#         if not self.responses:
#             return b""

#         response = self.responses.pop(0)
#         return response[:size]


# class OSErrorTransport:
#     def __init__(
#         self,
#         fail_on_write: bool = False,
#         fail_on_read: bool = False,
#     ):
#         self.fail_on_write = fail_on_write
#         self.fail_on_read = fail_on_read

#     def write(self, data: bytes) -> int:
#         if self.fail_on_write:
#             raise OSError("Simulated device disconnection.")

#     def read(self, size: int) -> bytes:
#         if self.fail_on_read:
#             raise OSError("Simulated device disconnection.")


# def create_test_driver(response_descriptor, data_response):
#     """
#     Creates a test driver with a mock transport that returns the
#     specified descriptor and data responses.
#     """
#     responses = [response_descriptor, data_response]
#     transport = MockTransport(responses)
#     return RPLidarDriver(transport)


# # Tests for driver get_info() method
# def test_get_info_with_valid_request_and_response():

#     response_descriptor = b"\xa5\x5a\x14\x00\x00\x00\x04"
#     data_response = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])
#     responses = [MOCK_GOOD_HEALTH_DESCRIPTOR, MOCK_GOOD_HEALTH_RESPONSE, response_descriptor, data_response]

#     transport = MockTransport(responses)
#     driver = RPLidarDriver(transport)

#     driver.connect()

#     info = driver.get_info()

#     assert driver._transport.written == bytes([0xA5, RPLidarCommand.GET_INFO.value])
#     assert info.model == 1
#     assert info.firmware_version_minor == 5
#     assert info.firmware_version_major == 2
#     assert info.hardware_version == 16
#     assert info.serial_number == bytes(range(16))


# def test_get_info_reads_invalid_start_flags():
#     descriptor = b"\x00\x00\x14\x00\x00\x00\x04"
#     data_response = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])

#     driver = create_test_driver(descriptor, data_response)

#     with pytest.raises(RPLidarProtocolError) as exc_info:
#         driver.get_info()

#     assert isinstance(exc_info.value.__cause__, ValueError)


# def test_get_info_with_invalid_response_descriptor_length():
#     # Size of data length is 21 bytes from bytes(0x15,0x00,0x00)
#     response_descriptor = b"\xa5\x5a\x15\x00\x00\x00\x04"
#     data_response = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])

#     driver = create_test_driver(response_descriptor, data_response)

#     with pytest.raises(RPLidarProtocolError):
#         driver.get_info()


# def test_get_info_with_invalid_descriptor_send_mode():

#     response_descriptor = b"\xa5\x5a\x14\x00\x00\x40\x04"
#     data_response = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])

#     driver = create_test_driver(response_descriptor, data_response)

#     with pytest.raises(RPLidarProtocolError):
#         driver.get_info()


# def test_get_info_with_invalid_descriptor_data_type():

#     # GET_INFO expectes 0x04 but receives 0x05
#     response_descriptor = b"\xa5\x5a\x14\x00\x00\x00\x05"
#     data_response = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])

#     driver = create_test_driver(response_descriptor, data_response)

#     with pytest.raises(RPLidarProtocolError):
#         driver.get_info()


# def test_get_info_preserves_binary_serial_number():

#     response_descriptor = b"\xa5\x5a\x14\x00\x00\x00\x04"
#     serial_number = bytes(
#         [
#             0xFF,
#             0x80,
#             0x7A,
#             0x00,
#             0x4B,
#             0x34,
#             0x28,
#             0xA2,
#             0x8A,
#             0x2F,
#             0x8E,
#             0x9F,
#             0x3A,
#             0x00,
#             0x24,
#             0x67,
#         ]
#     )

#     data_response = bytes([0x01, 0x05, 0x02, 0x10]) + serial_number

#     driver = create_test_driver(response_descriptor, data_response)

#     info = driver.get_info()

#     assert info.serial_number == serial_number


# def test_get_info_timeout_while_reading_descriptor():
#     mock_transport = MockTransport(
#         responses=[
#             b"\xa5\x5a\x14",  # Only 3 of the expected 7 bytes
#         ]
#     )

#     driver = RPLidarDriver(mock_transport)

#     with pytest.raises(
#         RPLidarTimeoutError,
#         match=r"GET_INFO descriptor expected 7 bytes but received 3 bytes",
#     ):
#         driver.get_info()


# def test_get_info_timeout_while_reading_data():
#     response_descriptor = b"\xa5\x5a\x14\x00\x00\x00\x04"
#     partial_data = bytes(
#         [
#             0x01,  # model
#             0x05,  # firmware minor
#             0x02,  # firmware major
#         ]
#     )

#     driver = create_test_driver(response_descriptor=response_descriptor, data_response=partial_data)

#     with pytest.raises(
#         RPLidarTimeoutError, match=r"GET_INFO expected 20 bytes but received 3 bytes"
#     ):
#         driver.get_info()


# # Tests for driver get_health() method
# def test_get_health_with_valid_request_and_response():
#     response_descriptor = b"\xa5\x5a\x03\x00\x00\x00\x06"
#     data_response = b"\x00\x01\x00"

#     driver = create_test_driver(
#         response_descriptor=response_descriptor, data_response=data_response
#     )

#     health = driver.get_health()

#     assert driver._transport.written == bytes([0xA5, RPLidarCommand.GET_HEALTH.value])
#     assert health.status == 0
#     assert health.error_code == 1


# def test_get_health_with_invalid_descriptor_size():
#     response_descriptor = b"\xa5\x5a\x03"
#     data_response = b"\x00\x01\x00"

#     driver = create_test_driver(
#         response_descriptor=response_descriptor, data_response=data_response
#     )

#     with pytest.raises(RPLidarTimeoutError):
#         driver.get_health()


# def test_get_health_with_invalid_descriptor_send_mode():
#     response_descriptor = b"\xa5\x5a\x03\x00\x00\x80\x06"  # Send mode received is 2
#     data_response = b"\x00\x01\x00"

#     driver = create_test_driver(
#         response_descriptor=response_descriptor, data_response=data_response
#     )

#     with pytest.raises(RPLidarProtocolError):
#         driver.get_health()


# def test_get_health_with_invalid_descriptor_data_type():
#     response_descriptor = (
#         b"\xa5\x5a\x03\x00\x00\x00\x05"  # GET_HEALTH expects 0x06 but receives 0x05
#     )
#     data_response = b"\x00\x01\x00"

#     driver = create_test_driver(
#         response_descriptor=response_descriptor, data_response=data_response
#     )

#     with pytest.raises(RPLidarProtocolError):
#         driver.get_health()


# def test_get_health_timeout_while_reading_descriptor():
#     mock_transport = MockTransport(
#         responses=[
#             b"\xa5\x5a\x03",
#         ]
#     )

#     driver = RPLidarDriver(mock_transport)

#     with pytest.raises(
#         RPLidarTimeoutError,
#         match=r"GET_HEALTH descriptor expected 7 bytes but received 3 bytes",
#     ):
#         driver.get_health()


# def test_get_health_timeout_while_reading_data():
#     response_descriptor = b"\xa5\x5a\x03\x00\x00\x00\x06"
#     partial_data = b"\x01\x02"

#     driver = create_test_driver(response_descriptor=response_descriptor, data_response=partial_data)

#     with pytest.raises(
#         RPLidarTimeoutError, match=r"GET_HEALTH expected 3 bytes but received 2 bytes"
#     ):
#         driver.get_health()


# def test_get_health_returns_warning_status():
#     response_descriptor = b"\xa5\x5a\x03\x00\x00\x00\x06"
#     data_response = b"\x01\x34\x12"

#     driver = create_test_driver(
#         response_descriptor=response_descriptor, data_response=data_response
#     )

#     health = driver.get_health()

#     assert health.status == 1
#     assert health.error_code == 0x1234


# def test_get_health_raises_error_status():
#     response_descriptor = b"\xa5\x5a\x03\x00\x00\x00\x06"
#     data_response = b"\x02\x34\x12"

#     driver = create_test_driver(
#         response_descriptor=response_descriptor, data_response=data_response
#     )

#     with pytest.raises(RPLidarDeviceError, match=r"RPLIDAR reported an internal error: 0x1234"):
#         driver.get_health()


# # Tests for driver get_samplerate() method
# def test_get_samplerate_with_valid_request_and_response():
#     response_descriptor = b"\xa5\x5a\x04\x00\x00\x00\x15"
#     data_response = b"\x01\x02\x34\x12"

#     driver = create_test_driver(
#         response_descriptor=response_descriptor, data_response=data_response
#     )

#     samplerate = driver.get_samplerate()

#     assert driver._transport.written == bytes([0xA5, RPLidarCommand.GET_SAMPLERATE.value])
#     assert samplerate.t_standard == 0x0201
#     assert samplerate.t_express == 0x1234


# def test_get_samplerate_with_invalid_descriptor_size():
#     response_descriptor = b"\xa5\x5a\x04"  # expects 7 bytes
#     data_response = b"\x00\x01\x00\x00"

#     driver = create_test_driver(
#         response_descriptor=response_descriptor, data_response=data_response
#     )

#     with pytest.raises(RPLidarTimeoutError):
#         driver.get_samplerate()


# def test_get_samplerate_with_invalid_descriptor_send_mode():
#     response_descriptor = b"\xa5\x5a\x04\x00\x00\x40\x15"  # Expects 0, receives 1.
#     data_response = b"\x00\x01\x00\x00"

#     driver = create_test_driver(
#         response_descriptor=response_descriptor, data_response=data_response
#     )

#     with pytest.raises(RPLidarProtocolError):
#         driver.get_samplerate()


# def test_get_samplerate_with_invalid_descriptor_data_type():
#     response_descriptor = b"\xa5\x5a\x04\x00\x00\x00\x80"  # Expects 0x15, but receives 0x80
#     data_response = b"\x00\x01\x12\x34"

#     driver = create_test_driver(
#         response_descriptor=response_descriptor, data_response=data_response
#     )

#     with pytest.raises(RPLidarProtocolError):
#         driver.get_samplerate()


# def test_get_samplerate_timeout_while_reading_descriptor():
#     mock_transport = MockTransport(
#         responses=[
#             b"\xa5\x5a\x04",
#         ]
#     )

#     driver = RPLidarDriver(mock_transport)

#     with pytest.raises(
#         RPLidarTimeoutError,
#         match=r"GET_SAMPLERATE descriptor expected 7 bytes but received 3 bytes",
#     ):
#         driver.get_samplerate()


# def test_get_samplerate_timeout_while_reading_data():
#     response_descriptor = b"\xa5\x5a\x04\x00\x00\x00\x15"
#     partial_data = b"\x12\x02"

#     driver = create_test_driver(response_descriptor=response_descriptor, data_response=partial_data)

#     with pytest.raises(
#         RPLidarTimeoutError,
#         match=r"GET_SAMPLERATE expected 4 bytes but received 2 bytes",
#     ):
#         driver.get_samplerate()


# # Tests for stop method
# def test_stop_valid_write():
#     transport = MockTransport()
#     driver = RPLidarDriver(transport)

#     driver.stop()

#     assert driver._transport.written == bytes([0xA5, RPLidarCommand.STOP.value])

# def test_stop_updates_scanning_state_and_pending_measurement():
#     """
#     Test stop() method correctly updates the scanning state and pending measurement.
#     """
#     responses = [
#         b"\xa5\x5a\x05\x00\x00\x40\x81",  # Response Descriptor for start_scan()
#         b"\xa6\x01\x00\x00\x00",  # Start Flag=0
#         b"\xa6\x01\x00\x00\x00",  # Start Flag=0
#         b"\xa6\x01\x00\x00\x00",  # Start Flag=0
#         b"\xa5\x95\x12\xc8\x03",  # Start Flag=1
#         b"\x96\x01\xb2\xff\xff",  # Start Flag=0
#         b"\xa6\x01\x00\x00\x00",  # Start Flag=0
#         b"\xa6\x2b\x15\xb1\xa2",  # Start Flag=0
#         b"\xa5\x01\x00\x00\x00",  # Start Flag=1
#     ]

#     transport = MockTransport(responses)
#     driver = RPLidarDriver(transport)

#     driver.start_scan()
#     scan = driver.read_scan() # Read the scan data to populate the pending measurement

#     driver.stop()

#     assert not driver.scanning_state.is_active
#     assert driver.scanning_state.packet_size == 0
#     assert driver.scanning_state.response_type is None
#     assert driver.scanning_state.mode is None
#     assert driver.working_state == RPLidarWorkingState.IDLE
#     assert driver._pending_measurement is None

# @patch("rtrpp.sensors.rplidar.driver.time.sleep")
# def test_stop_waits_before_returning(mock_sleep):
#     transport = MockTransport()
#     driver = RPLidarDriver(transport)

#     driver.stop()

#     mock_sleep.assert_called_once_with(0.001)


# # Tests for reset method
# def test_reset_valid_write():
#     transport = MockTransport()
#     driver = RPLidarDriver(transport)

#     driver.reset()

#     assert driver._transport.written == bytes([0xA5, RPLidarCommand.RESET.value])


# @patch("rtrpp.sensors.rplidar.driver.time.sleep")
# def test_reset_waits_before_returning(mock_sleep):
#     transport = MockTransport()
#     driver = RPLidarDriver(transport)

#     driver.reset()

#     mock_sleep.assert_called_once_with(0.002)


# # Tests for start_scan() method
# def test_start_scan_with_valid_request_and_descriptor():

#     descriptor = b"\xa5\x5a\x05\x00\x00\x40\x81"

#     driver = create_test_driver(response_descriptor=descriptor, data_response=b"")

#     driver.start_scan()

#     assert driver._transport.written == bytes([0xA5, RPLidarCommand.SCAN.value])
#     assert driver.scanning_state.is_active
#     assert driver.scanning_state.packet_size == RPLidarDataLength.SCAN_DATA.value
#     assert driver.scanning_state.mode == RPLidarScanningMode.STANDARD
#     assert driver.scanning_state.response_type == RPLidarResponseType.MEASUREMENT_DATA
#     assert driver.working_state == RPLidarWorkingState.SCANNING


# def test_start_scan_with_invalid_descriptor_size():

#     invalid_descriptor = b"\xa5\x5a\x05"

#     driver = create_test_driver(response_descriptor=invalid_descriptor, data_response=b"")

#     with pytest.raises(RPLidarTimeoutError):
#         driver.start_scan()


# def test_start_scan_with_invalid_descriptor_send_mode():

#     invalid_descriptor = b"\xa5\x5a\x05\x00\x00\x00\x81"  # Expects 1, receives 0.

#     driver = create_test_driver(response_descriptor=invalid_descriptor, data_response=b"")

#     with pytest.raises(RPLidarProtocolError):
#         driver.start_scan()


# def test_start_scan_with_invalid_data_type():

#     invalid_descriptor = b"\xa5\x5a\x05\x00\x00\x40\x15"  # Expects 0x81, but receives 0x15

#     driver = create_test_driver(response_descriptor=invalid_descriptor, data_response=b"")

#     with pytest.raises(RPLidarProtocolError):
#         driver.start_scan()


# def test_start_scan_timeout_while_reading_descriptor():

#     invalid_descriptor = b"\xa5\x5a\x05\x00"

#     driver = create_test_driver(response_descriptor=invalid_descriptor, data_response=b"")

#     with pytest.raises(
#         RPLidarTimeoutError, match=r"SCAN descriptor expected 7 bytes but received 4 bytes."
#     ):
#         driver.start_scan()


# # Tests for read_scan() method
# def test_read_scan_with_valid_response_data():
#     """
#     Test reading scan data and verify boundary measurement(start of next scan
#     saves in _pending_measurement.
#     """
#     responses = [
#         b"\xa5\x5a\x05\x00\x00\x40\x81",  # Response Descriptor for start_scan()
#         b"\xa6\x01\x00\x00\x00",  # Start Flag=1
#         b"\xa5\x01\x00\x00\x00",  # Start Flag=0
#         b"\xa6\x01\x00\x00\x00",  # Start Flag=0
#         b"\xa5\x95\x12\xc8\x03",  # Boundary measurement (start of next scan)
#         b"\x96\x01\xb2\xff\xff",
#         b"\xa6\x01\x00\x00\x00",
#         b"\xa6\x2b\x15\xb1\xa2",
#         b"\xa5\x01\x00\x00\x00",
#     ]

#     transport = MockTransport(responses)
#     driver = RPLidarDriver(transport)

#     driver.start_scan()
#     scan = driver.read_scan()
#     scan = driver.read_scan()

#     assert scan[0].start_flag is True
#     assert scan[0].quality == 41
#     assert scan[0].angle_degrees == pytest.approx(37.15625)
#     assert scan[0].distance_mm == pytest.approx(242.0)

#     assert scan[1].start_flag is False
#     assert scan[1].quality == 37
#     assert scan[1].angle_degrees == pytest.approx(356.0)
#     assert scan[1].distance_mm == pytest.approx(16383.75)

#     assert scan[-1].start_flag is False
#     assert scan[-1].quality == 41
#     assert scan[-1].angle_degrees == pytest.approx(42.32812)
#     assert scan[-1].distance_mm == pytest.approx(10412.25)

#     assert len(scan) == 4

#     # Verify that the boundary measurement is saved in _pending_measurement
#     assert driver._pending_measurement.start_flag is True
#     assert driver._pending_measurement.quality == 41
#     assert driver._pending_measurement.angle_degrees == 0
#     assert driver._pending_measurement.distance_mm == 0


# def test_read_scan_waits_for_new_scan():
#     responses = [
#         b"\xa5\x5a\x05\x00\x00\x40\x81",  # Response Descriptor for start_scan()
#         b"\xa6\x01\x00\x00\x00",  # Start Flag=0
#         b"\xa6\x01\x00\x00\x00",  # Start Flag=0
#         b"\xa6\x01\x00\x00\x00",  # Start Flag=0
#         b"\xa5\x95\x12\xc8\x03",  # Start Flag=1
#         b"\x96\x01\xb2\xff\xff",  # Start Flag=0
#         b"\xa6\x01\x00\x00\x00",  # Start Flag=0
#         b"\xa6\x2b\x15\xb1\xa2",  # Start Flag=0
#         b"\xa5\x01\x00\x00\x00",  # Start Flag=1
#     ]

#     transport = MockTransport(responses)
#     driver = RPLidarDriver(transport)

#     driver.start_scan()
#     scan = driver.read_scan()

#     assert scan[0].start_flag is True
#     assert scan[0].quality == 41
#     assert scan[0].angle_degrees == pytest.approx(37.15625)
#     assert scan[0].distance_mm == pytest.approx(242.0)

#     assert scan[1].start_flag is False
#     assert scan[1].quality == 37
#     assert scan[1].angle_degrees == pytest.approx(356.0)
#     assert scan[1].distance_mm == pytest.approx(16383.75)

#     assert scan[-1].start_flag is False
#     assert scan[-1].quality == 41
#     assert scan[-1].angle_degrees == pytest.approx(42.328125)
#     assert scan[-1].distance_mm == pytest.approx(10412.25)


# def test_read_scan_with_invalid_measurement_data_length():
#     responses = [
#         b"\xa5\x5a\x05\x00\x00\x40\x81",
#         b"\xa5\x95\x12",
#     ]

#     transport = MockTransport(responses)
#     driver = RPLidarDriver(transport)

#     driver.start_scan()

#     with pytest.raises(
#         RPLidarTimeoutError,
#         match=r"SCAN measurement expected 5 bytes but received 3 bytes",
#     ):
#         driver.read_scan()


# def test_read_scan_with_invalid_start_flags():
#     responses = [
#         b"\xa5\x5a\x05\x00\x00\x40\x81",
#         b"\xa5\x95\x12\xc8\x03",
#         b"\xa6\x01\x00\x00\x00",
#         b"\x00\x01\x00\x00\x00",  # Start Flag=0, !Start Flag=0
#         b"\xa6\x2b\x15\xb1\xa2",
#         b"\xa5\x01\x00\x00\x00",
#     ]

#     transport = MockTransport(responses)
#     driver = RPLidarDriver(transport)

#     driver.start_scan()

#     with pytest.raises(RPLidarProtocolError) as exc_info:
#         driver.read_scan()

#     assert isinstance(exc_info.value.__cause__, ValueError)


# def test_read_scan_with_invalid_check_bit():
#     responses = [
#         b"\xa5\x5a\x05\x00\x00\x40\x81",  # Response Descriptor for start_scan()
#         b"\xa6\x00\x00\x00\x00",  # Expects Check Bit 1, receives 0.
#         b"\xa5\x01\x00\x00\x00",
#     ]

#     transport = MockTransport(responses)
#     driver = RPLidarDriver(transport)

#     driver.start_scan()

#     with pytest.raises(RPLidarProtocolError) as exc_info:
#         driver.read_scan()

#     assert isinstance(exc_info.value.__cause__, ValueError)


# @pytest.mark.parametrize(
#     "operation",
#     [
#         lambda driver: driver.get_info(),
#         lambda driver: driver.get_health(),
#         lambda driver: driver.get_samplerate(),
#         lambda driver: driver.stop(),
#         lambda driver: driver.reset(),
#         lambda driver: driver.start_scan(),
#     ],
# )
# def test_driver_translates_serial_write_failure(operation):
#     transport = MockTransport(fail_on_write=True)
#     driver = RPLidarDriver(transport)

#     with pytest.raises(RPLidarConnectionError) as exc_info:
#         operation(driver)

#     assert isinstance(exc_info.value.__cause__, serial.SerialException)


# @pytest.mark.parametrize(
#     "operation",
#     [
#         lambda driver: driver.get_info(),
#         lambda driver: driver.get_health(),
#         lambda driver: driver.get_samplerate(),
#         lambda driver: driver.start_scan(),
#         lambda driver: driver._read_measurement(),
#     ],
# )
# def test_driver_translates_serial_read_failure(operation):
#     transport = MockTransport(fail_on_read=True)
#     driver = RPLidarDriver(transport)

#     with pytest.raises(RPLidarConnectionError) as exc_info:
#         operation(driver)

#     assert isinstance(exc_info.value.__cause__, serial.SerialException)


# @pytest.mark.parametrize(
#     "operation",
#     [
#         lambda driver: driver.get_info(),
#         lambda driver: driver.get_health(),
#         lambda driver: driver.get_samplerate(),
#         lambda driver: driver.stop(),
#         lambda driver: driver.reset(),
#         lambda driver: driver.start_scan(),
#     ],
# )
# def test_driver_translates_oserror_during_write(operation):
#     transport = OSErrorTransport(fail_on_write=True)
#     driver = RPLidarDriver(transport)

#     with pytest.raises(RPLidarConnectionError) as exc_info:
#         operation(driver)

#     assert isinstance(exc_info.value.__cause__, OSError)


# @pytest.mark.parametrize(
#     "operation",
#     [
#         lambda driver: driver.get_info(),
#         lambda driver: driver.get_health(),
#         lambda driver: driver.get_samplerate(),
#         lambda driver: driver.start_scan(),
#         lambda driver: driver._read_measurement(),
#     ],
# )
# def test_driver_translates_oserror_during_read(operation):
#     transport = OSErrorTransport(fail_on_read=True)
#     driver = RPLidarDriver(transport)

#     with pytest.raises(RPLidarConnectionError) as exc_info:
#         operation(driver)

#     assert isinstance(exc_info.value.__cause__, OSError)
