import pytest

from rtrpp.sensors.rplidar.protocol import (
    RPLidarCommand,
    RPLidarScanData,
    RPLidarGetInfoData,
    RPLidarGetHealthData,
    RPLidarGetSamplerateData,
)

from rtrpp.sensors.rplidar.exceptions import (
    TransportConnectionError,
    TransportTimeoutError,
    RPLidarStateError,
    RPLidarConnectionError,
    RPLidarTimeoutError,
    RPLidarDeviceError,
    RPLidarProtocolError,
)

from tests.sensors.rplidar.test_support.fakes import (
    queue_get_info_response,
    queue_get_health_response,
)

from tests.sensors.rplidar.driver.assertions import (
    assert_idle_invariants,
    assert_not_connected_invariants,
    assert_protection_stop_invariants,
    assert_transport_untouched,
)


# get_info - successful outcomes
def test_get_info_valid_request_and_response(idle_driver):
    driver, transport = idle_driver

    queue_get_info_response(
        transport,
        model=112,
        firmware_version_minor=1,
        firmware_version_major=18,
        hardware_version=2,
        serial_number = b"\xe2d\xe0\xf6\xc1\xe0\x92\xd8\xa1\x9e\x9f\xf9r\xc8F\x16"
    )

    info = driver.get_info()

    assert transport.written == bytes([0xA5, RPLidarCommand.GET_INFO.value])

    assert info.model == 112
    assert info.firmware_version_minor == 1
    assert info.firmware_version_major == 18
    assert info.hardware_version == 2
    assert info.serial_number == b"\xe2d\xe0\xf6\xc1\xe0\x92\xd8\xa1\x9e\x9f\xf9r\xc8F\x16"

    assert_idle_invariants(driver)

def test_get_info_valid_request_and_response_in(protection_stop_driver):
    driver, transport = protection_stop_driver

    queue_get_info_response(
        transport,
        model=10,
        firmware_version_minor=12,
        firmware_version_major=1,
        hardware_version=3,
        serial_number=b"\xe2d\xe0\xf6\xc1\xe0\x00\x00\xa1\x9e\x9f\xf9r\xc8F\x16"
    )

    info = driver.get_info()

    assert transport.written == bytes([0xA5, RPLidarCommand.GET_INFO.value])

    assert info.model == 10
    assert info.firmware_version_minor == 12
    assert info.firmware_version_major == 1
    assert info.hardware_version == 3
    assert info.serial_number == b"\xe2d\xe0\xf6\xc1\xe0\x00\x00\xa1\x9e\x9f\xf9r\xc8F\x16"

    assert_protection_stop_invariants(driver)


# get_info - invalid state

def test_get_info_state_error_with_invalid_starting_state(not_connected_driver):
    driver, transport = not_connected_driver

    with pytest.raises(
        RPLidarStateError,
        match="Operation requires working state "
    ):
        driver.get_info()

    assert_not_connected_invariants(driver)
    assert_transport_untouched(transport)


# get_info - query failures
def test_get_info_reads_invalid_start_flags(idle_driver):
    driver, transport = idle_driver

    descriptor = b"\x00\x00\x14\x00\x00\x00\x04"
    payload = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])
    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError, match="Invalid response descriptor start flags"
    ) as exc_info:
        driver.get_info()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)


def test_get_info_receives_invalid_descriptor_response_length(idle_driver):
    driver, transport = idle_driver

    descriptor = b"\xa5\x5a\x15\x00\x00\x00\x04"
    payload = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])

    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError, 
        match="GET_INFO expected 20 response bytes, received descriptor length 21."
    ) as exc_info:
        driver.get_info()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)


def test_get_info_receives_invalid_descriptor_send_mode(idle_driver):
    driver, tranport = idle_driver

    descriptor = b"\xa5\x5a\x14\x00\x00\x40\x04"
    payload = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])

    tranport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError, match="GET_INFO expected send mode 0, but got 1"
    ) as exc_info:
        driver.get_info()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)


def test_get_info_receives_invalid_descriptor_data_type(idle_driver):
    driver, tranport = idle_driver

    descriptor = b"\xa5\x5a\x14\x00\x00\x00\x05"
    payload = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])

    tranport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError, match="GET_INFO expected data type 4, but got 5"
    ) as exc_info:
        driver.get_info()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)

  
# get_info - connection failures
def test_get_info_timeout_enters_idle_state(idle_driver):
    driver, transport = idle_driver

    queue_get_info_response(
        transport,
    )

    transport.fail_read = TransportTimeoutError("Timeout while reading")

    with pytest.raises(RPLidarTimeoutError, match="while reading"):
        driver.get_info()

    assert_idle_invariants(driver)
    assert transport.is_open is True


def test_get_info_connection_error_moves_to_not_connected(idle_driver):
    driver, transport = idle_driver

    queue_get_info_response(transport)

    transport.fail_write = TransportConnectionError("Failed while requesting")

    with pytest.raises(RPLidarConnectionError, match="while requesting") as exc_info:
        driver.get_info()

    assert isinstance(exc_info.value.__cause__, TransportConnectionError)
    assert_not_connected_invariants(driver)
    assert transport.is_open is False



    