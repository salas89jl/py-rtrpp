from unittest.mock import patch

import pytest


from rtrpp.sensors.rplidar.protocol import (
    RPLidarCommand,
)

from rtrpp.sensors.rplidar.exceptions import (
    RPLidarConnectionError,
    RPLidarDeviceError,
    RPLidarProtocolError,
    RPLidarStateError,
    RPLidarTimeoutError,
    TransportConnectionError,
    TransportTimeoutError,
)

from rtrpp.sensors.rplidar.rplidar_warnings import RPLidarHealthWarning
from tests.sensors.rplidar.test_support.fakes import (
    queue_get_health_response,
    queue_get_info_response,
)

from tests.sensors.rplidar.driver.assertions import (
    assert_idle_invariants,
    assert_not_connected_invariants,
    assert_protection_stop_invariants,
    assert_transport_synced,
    assert_transport_untouched,
    assert_scanning_invariants,
    assert_transport_closed_in_connection_error,
    assert_transport_did_not_sync_in_connection_error,
)


# ---------------------------------------Test get_info()----------------------------------------#


# get_info - successful outcomes
def test_get_info_valid_request_and_response(idle_driver):
    driver, transport = idle_driver

    queue_get_info_response(
        transport,
        model=112,
        firmware_version_minor=1,
        firmware_version_major=18,
        hardware_version=2,
        serial_number=b"\xe2d\xe0\xf6\xc1\xe0\x92\xd8\xa1\x9e\x9f\xf9r\xc8F\x16",
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
        serial_number=b"\xe2d\xe0\xf6\xc1\xe0\x00\x00\xa1\x9e\x9f\xf9r\xc8F\x16",
    )

    info = driver.get_info()

    assert transport.written == bytes([0xA5, RPLidarCommand.GET_INFO.value])

    assert info.model == 10
    assert info.firmware_version_minor == 12
    assert info.firmware_version_major == 1
    assert info.hardware_version == 3
    assert info.serial_number == b"\xe2d\xe0\xf6\xc1\xe0\x00\x00\xa1\x9e\x9f\xf9r\xc8F\x16"

    assert_protection_stop_invariants(driver)


# get_info - query protocol failures
def test_get_info_reads_invalid_start_flags(idle_driver):
    driver, transport = idle_driver

    descriptor = b"\x00\x00\x14\x00\x00\x00\x04"  # Expects 0xA5, 0x5A
    payload = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])
    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError, match="Invalid response descriptor start flags"
    ) as exc_info:
        driver.get_info()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)  # starting state remains unchanged


def test_get_info_receives_invalid_descriptor_response_length_in_idle(
    idle_driver,
):
    driver, transport = idle_driver

    descriptor = b"\xa5\x5a\x15\x00\x00\x00\x04"  # Expects 20 bytes, received 21
    payload = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])

    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError,
        match="GET_INFO expected 20 response bytes, received descriptor length 21.",
    ) as exc_info:
        driver.get_info()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)  # starting state remains unchanged


def test_get_info_receives_invalid_descriptor_response_length_in_protection_stop(
    protection_stop_driver,
):
    driver, transport = protection_stop_driver

    descriptor = b"\xa5\x5a\x15\x00\x00\x00\x04"  # Expects 20 bytes, received 21
    payload = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])

    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError,
        match="GET_INFO expected 20 response bytes, received descriptor length 21.",
    ) as exc_info:
        driver.get_info()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_protection_stop_invariants(driver)  # starting state remains unchanged


def test_get_info_receives_invalid_descriptor_send_mode(idle_driver):
    driver, transport = idle_driver

    descriptor = b"\xa5\x5a\x14\x00\x00\x40\x04"  # Expects (0), receives (1)
    payload = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])

    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError, match="GET_INFO expected send mode 0, but got 1"
    ) as exc_info:
        driver.get_info()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)  # starting state remains unchanged


def test_get_info_receives_invalid_descriptor_data_type(idle_driver):
    driver, transport = idle_driver

    descriptor = b"\xa5\x5a\x14\x00\x00\x00\x05"  # Expects 0x04 (4), received 0x05 (5)
    payload = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])

    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError, match="GET_INFO expected data type 4, but got 5"
    ) as exc_info:
        driver.get_info()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)  # starting state remains unchanged


# ---------------------------------------Test get_health()----------------------------------------#


# get_health - successful outcomes
def test_get_health_valid_request_and_returns_good_health(idle_driver):
    driver, transport = idle_driver

    queue_get_health_response(
        transport,
        status=0,
        error_code=0x0000,
    )

    health = driver.get_health()

    assert transport.written == bytes([0xA5, RPLidarCommand.GET_HEALTH.value])

    assert health.status == 0
    assert health.error_code == 0x0000

    assert_idle_invariants(driver)


def test_get_health_returns_valid_warning_health(idle_driver):
    driver, transport = idle_driver

    queue_get_health_response(
        transport,
        status=1,
        error_code=0x1234,
    )

    with pytest.warns(RPLidarHealthWarning, match="potential risk"):
        health = driver.get_health()

    assert transport.written == bytes([0xA5, RPLidarCommand.GET_HEALTH.value])

    assert health.status == 1
    assert health.error_code == 0x1234

    assert_idle_invariants(driver)


def test_get_health_valid_request_and_returns_error_health(protection_stop_driver):
    driver, transport = protection_stop_driver

    queue_get_health_response(
        transport,
        status=2,
        error_code=0x5678,
    )

    health = driver.get_health()

    assert transport.written == bytes([0xA5, RPLidarCommand.GET_HEALTH.value])

    assert health.status == 2
    assert health.error_code == 0x5678

    assert_protection_stop_invariants(driver)


def test_get_health_valid_request_and_returns_error_health_in_idle(idle_driver):
    driver, transport = idle_driver

    queue_get_health_response(
        transport,
        status=2,
        error_code=0x5678,
    )

    health = driver.get_health()

    assert transport.written == bytes([0xA5, RPLidarCommand.GET_HEALTH.value])

    assert health.status == 2
    assert health.error_code == 0x5678

    assert_idle_invariants(driver)


def test_get_health_valid_request_and_returns_warning_health_in_idle(idle_driver):
    driver, transport = idle_driver

    queue_get_health_response(
        transport,
        status=1,
        error_code=0x5678,
    )
    with pytest.warns(RPLidarHealthWarning, match="potential risk"):
        health = driver.get_health()

    assert transport.written == bytes([0xA5, RPLidarCommand.GET_HEALTH.value])

    assert health.status == 1
    assert health.error_code == 0x5678

    assert_idle_invariants(driver)


def test_get_health_valid_request_and_returns_warning_health_in_protection_stop(protection_stop_driver):
    driver, transport = protection_stop_driver

    queue_get_health_response(
        transport,
        status=1,
        error_code=0x5678,
    )

    with pytest.warns(RPLidarHealthWarning, match="potential risk"):
        health = driver.get_health()

    assert transport.written == bytes([0xA5, RPLidarCommand.GET_HEALTH.value])

    assert health.status == 1
    assert health.error_code == 0x5678

    assert_protection_stop_invariants(driver)


def test_get_health_valid_request_and_returns_good_health_in_protection_stop(
    protection_stop_driver,
):
    driver, transport = protection_stop_driver

    queue_get_health_response(
        transport,
        status=0,
        error_code=0x0000,
    )

    health = driver.get_health()

    assert transport.written == bytes([0xA5, RPLidarCommand.GET_HEALTH.value])

    assert health.status == 0
    assert health.error_code == 0x0000

    assert_protection_stop_invariants(driver)


# get_health - query protocol failures
def test_get_health_reads_invalid_start_flags(idle_driver):
    driver, transport = idle_driver

    descriptor = b"\xa5\xa5\x03\x00\x00\x00\x06"  # Expects 0xA5, 0x5A
    payload = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])
    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError, match="Invalid response descriptor start flags"
    ) as exc_info:
        driver.get_health()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)


def test_get_health_receives_invalid_descriptor_response_length(idle_driver):
    driver, transport = idle_driver

    descriptor = b"\xa5\x5a\x15\x00\x00\x00\x06"  # Expects 0x03 (3), received 0x15 (21)
    payload = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])

    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError,
        match="GET_HEALTH expected 3 response bytes, received descriptor length 21.",
    ) as exc_info:
        driver.get_health()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)


def test_get_health_receives_invalid_descriptor_send_mode(idle_driver):
    driver, transport = idle_driver

    descriptor = b"\xa5\x5a\x03\x00\x00\x40\x06"  # Expects (0), receives (1)
    payload = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])

    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError, match="GET_HEALTH expected send mode 0, but got 1"
    ) as exc_info:
        driver.get_health()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)


def test_get_health_receives_invalid_descriptor_data_type(idle_driver):
    driver, transport = idle_driver

    descriptor = b"\xa5\x5a\x03\x00\x00\x00\x07"  # Expects 0x06 (6), received 0x07 (7)
    payload = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])

    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError, match="GET_HEALTH expected data type 6, but got 7"
    ) as exc_info:
        driver.get_health()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)


def test_get_health_receives_invalid_status_value(idle_driver):
    driver, transport = idle_driver

    queue_get_health_response(
        transport,
        status=5,  # Invalid status value
        error_code=0x1234,
    )

    with pytest.raises(
        RPLidarProtocolError, match="Invalid GET_HEALTH status value: 5"
    ) as exc_info:
        driver.get_health()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)


# -------------------------------------Test get_samplerate()--------------------------------------#


# get_samplerate - successful outcomes
def test_get_samplerate_valid_request_and_response(idle_driver):
    driver, transport = idle_driver

    descriptor = b"\xa5\x5a\x04\x00\x00\x00\x15"
    payload = bytes([0x01, 0x02, 0x34, 0x12])

    transport.responses.extend([descriptor, payload])

    samplerate = driver.get_samplerate()

    assert transport.written == bytes([0xA5, RPLidarCommand.GET_SAMPLERATE.value])

    assert samplerate.t_standard == 0x0201
    assert samplerate.t_express == 0x1234


def test_get_samplerate_valid_request_and_response_in(protection_stop_driver):
    driver, transport = protection_stop_driver

    descriptor = b"\xa5\x5a\x04\x00\x00\x00\x15"
    payload = bytes([0x01, 0x02, 0x34, 0x12])

    transport.responses.extend([descriptor, payload])

    samplerate = driver.get_samplerate()

    assert transport.written == bytes([0xA5, RPLidarCommand.GET_SAMPLERATE.value])

    assert samplerate.t_standard == 0x0201
    assert samplerate.t_express == 0x1234


# get_samplerate - query protocol failures
def test_get_samplerate_reads_invalid_start_flags(idle_driver):
    driver, transport = idle_driver

    descriptor = b"\x00\x00\x04\x00\x00\x00\x15"
    payload = bytes([0x01, 0x02, 0x34, 0x12])
    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError, match="Invalid response descriptor start flags"
    ) as exc_info:
        driver.get_samplerate()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)


def test_get_samplerate_receives_invalid_descriptor_response_length(idle_driver):
    driver, transport = idle_driver

    descriptor = b"\xa5\x5a\x05\x00\x00\x00\x15"  # Expects 0x04 (4), received 0x05 (5)
    payload = bytes([0x01, 0x02, 0x34, 0x12])

    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError,
        match="GET_SAMPLERATE expected 4 response bytes, received descriptor length 5.",
    ) as exc_info:
        driver.get_samplerate()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)


def test_get_samplerate_receives_invalid_descriptor_send_mode(idle_driver):
    driver, transport = idle_driver

    descriptor = b"\xa5\x5a\x04\x00\x00\x40\x15"  # Expects (0), receives (1)
    payload = bytes([0x01, 0x02, 0x34, 0x12])

    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError, match="GET_SAMPLERATE expected send mode 0, but got 1"
    ) as exc_info:
        driver.get_samplerate()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)


def test_get_samplerate_receives_invalid_descriptor_data_type(idle_driver):
    driver, transport = idle_driver

    descriptor = b"\xa5\x5a\x04\x00\x00\x00\x16"  # Expects 0x15 (21), received 0x16 (22)
    payload = bytes([0x01, 0x02, 0x34, 0x12])

    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError, match="GET_SAMPLERATE expected data type 21, but got 22"
    ) as exc_info:
        driver.get_samplerate()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)


# ---------------------------------------Test stop()----------------------------------------#


# stop - successful outcomes
def test_stop_valid_request_and_response(scanning_driver):
    driver, transport = scanning_driver

    driver.stop()

    assert transport.written == bytes([0xA5, RPLidarCommand.STOP.value])
    assert_idle_invariants(driver)


@patch("rtrpp.sensors.rplidar.driver.time.sleep")
def test_stop_waits_before_transitioning_to_idle(mock_sleep, scanning_driver):
    driver, transport = scanning_driver

    driver.stop()

    mock_sleep.assert_called_once_with(0.001)
    assert_idle_invariants(driver)


# ---------------------------------------Test reset()----------------------------------------#


# reset - successful outcomes
def test_reset_valid_request_and_response(protection_stop_driver):
    driver, transport = protection_stop_driver

    queue_get_health_response(transport, status=0, error_code=0x0000)

    driver.reset()

    assert transport.written == bytes(
        [0xA5, RPLidarCommand.RESET.value, 0xA5, RPLidarCommand.GET_HEALTH.value]
    )

    assert_idle_invariants(driver)


@patch("rtrpp.sensors.rplidar.driver.time.sleep")
def test_reset_waits_before_transitioning_to_idle(mock_sleep, protection_stop_driver):
    driver, transport = protection_stop_driver

    queue_get_health_response(transport, status=0, error_code=0x0000)

    driver.reset()

    mock_sleep.assert_called_once_with(0.002)
    assert_idle_invariants(driver)

# ---------------------------------------Test _check_health()-----------------------------------#

## _check_health - successful outcomes

### Starting state is `IDLE`:
def test_check_health_warns_on_good_health_in_idle_state(idle_driver):
    driver, transport = idle_driver

    queue_get_health_response(
        transport,
        status=0,
        error_code=0x0000,
    )

    driver._check_health()

    assert transport.written == bytes([0xA5, RPLidarCommand.GET_HEALTH.value])
    assert driver._health.status == 0
    assert driver._health.error_code == 0x0000
    assert_idle_invariants(driver)  


def test_check_health_warns_on_warning_health_in_idle_state(idle_driver):
    driver, transport = idle_driver

    queue_get_health_response(
        transport,
        status=1,
        error_code=0x1234,
    )

    with pytest.warns(RPLidarHealthWarning, match="potential risk"):
        driver._check_health()

    assert transport.written == bytes([0xA5, RPLidarCommand.GET_HEALTH.value])
    assert driver._health.status == 1
    assert driver._health.error_code == 0x1234
    assert_idle_invariants(driver)


def test_check_health_raises_error_on_error_health_in_idle_state_and_transitions_to_protection_stop(
        idle_driver
):
    driver, transport = idle_driver

    queue_get_health_response(
        transport,
        status=2,
        error_code=0x5678,
    )

    with pytest.raises(RPLidarDeviceError, match="RPLIDAR reported an internal error"):
        driver._check_health()

    assert transport.written == bytes([0xA5, RPLidarCommand.GET_HEALTH.value])
    assert driver._health.status == 2
    assert driver._health.error_code == 0x5678
    assert_protection_stop_invariants(driver)


### Starting state is `PROTECTION_STOP`:
def test_check_health_caches_good_health_in_protection_stop_state(protection_stop_driver):
    driver, transport = protection_stop_driver

    queue_get_health_response(
        transport,
        status=0,
        error_code=0x0000,
    )

    driver._check_health()

    assert transport.written == bytes([0xA5, RPLidarCommand.GET_HEALTH.value])
    assert driver._health.status == 0
    assert driver._health.error_code == 0x0000

    # Starting state remains unchanged - recovery must be explicitly invoked by the caller
    assert_protection_stop_invariants(driver) 




def test_check_health_warns_on_warning_health_in_protection_stop_state(protection_stop_driver):
    driver, transport = protection_stop_driver

    queue_get_health_response(
        transport,
        status=1,
        error_code=0x5678,
    )

    with pytest.warns(RPLidarHealthWarning, match="potential risk"):
        driver._check_health()

    assert transport.written == bytes([0xA5, RPLidarCommand.GET_HEALTH.value])
    assert driver._health.status == 1
    assert driver._health.error_code == 0x5678

    # Starting state remains unchanged - recovery must be explicitly invoked by the caller
    assert_protection_stop_invariants(driver)


def test_check_health_raises_error_on_error_health_in_protection_stop_state(protection_stop_driver):
    driver, transport = protection_stop_driver

    queue_get_health_response(
        transport,
        status=2,
        error_code=0x5678,
    )

    with pytest.raises(RPLidarDeviceError, match="RPLIDAR reported an internal error"):
        driver._check_health()

    assert transport.written == bytes([0xA5, RPLidarCommand.GET_HEALTH.value])
    assert driver._health.status == 2
    assert driver._health.error_code == 0x5678
    assert_protection_stop_invariants(driver) # Starting state remains unchanged


## _check_health - query protocol failures
def test_check_health_reads_invalid_start_flags(idle_driver):
    driver, transport = idle_driver

    descriptor = b"\x00\x00\x03\x00\x00\x00\x06"  # Expects 0xA5, 0x5A
    payload = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])
    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError, match="Invalid response descriptor start flags"
    ) as exc_info:
        driver._check_health()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)  # starting state remains unchanged

def test_check_health_receives_invalid_descriptor_response_length(idle_driver):
    driver, transport = idle_driver

    descriptor = b"\xa5\x5a\x15\x00\x00\x00\x06"  # Expects 0x03 (3), received 0x15 (21)
    payload = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])

    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError,
        match="GET_HEALTH expected 3 response bytes, received descriptor length 21.",
    ) as exc_info:
        driver._check_health()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)  # starting state remains unchanged

def test_check_health_receives_invalid_descriptor_send_mode(idle_driver):
    driver, transport = idle_driver

    descriptor = b"\xa5\x5a\x03\x00\x00\x40\x06"  # Expects (0), receives (1)
    payload = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])

    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError, match="GET_HEALTH expected send mode 0, but got 1"
    ) as exc_info:
        driver._check_health()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)  # starting state remains unchanged


def test_check_health_receives_invalid_descriptor_data_type(idle_driver):
    driver, transport = idle_driver

    descriptor = b"\xa5\x5a\x03\x00\x00\x00\x07"  # Expects 0x06 (6), received 0x07 (7)
    payload = bytes([0x01, 0x05, 0x02, 0x10, *range(16)])

    transport.responses.extend([descriptor, payload])

    with pytest.raises(
        RPLidarProtocolError, match="GET_HEALTH expected data type 6, but got 7"
    ) as exc_info:
        driver._check_health()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)  # starting state remains unchanged

def test_check_health_receives_invalid_status_value(idle_driver):
    driver, transport = idle_driver

    queue_get_health_response(
        transport,
        status=5,  # Invalid status value
        error_code=0x1234,
    )

    with pytest.raises(
        RPLidarProtocolError, match="Invalid GET_HEALTH status value: 5"
    ) as exc_info:
        driver._check_health()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_idle_invariants(driver)  # starting state remains unchanged

def test_check_health_receives_invalid_status_value_in_protection_stop(protection_stop_driver):
    driver, transport = protection_stop_driver

    queue_get_health_response(
        transport,
        status=5,  # Invalid status value
        error_code=0x1234,
    )

    with pytest.raises(
        RPLidarProtocolError, match="Invalid GET_HEALTH status value: 5"
    ) as exc_info:
        driver._check_health()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_protection_stop_invariants(driver)  # starting state remains unchanged

# ---------------------------------------State failures-----------------------------------------#


# Query methods - invalid starting state(NOT_CONNECTED)
@pytest.mark.parametrize(
    "operation",
    [
        lambda driver: driver.get_info(),
        lambda driver: driver.get_health(),
        lambda driver: driver.get_samplerate(),
        lambda driver: driver.stop(),
        lambda driver: driver.reset(),
        lambda driver: driver._check_health(),
    ],
)
def test_query_methods_raise_invalid_state_error_when_not_connected(
    operation,
    not_connected_driver,
):
    driver, transport = not_connected_driver

    with pytest.raises(RPLidarStateError, match="Operation requires working state"):
        operation(driver)

    assert_transport_untouched(transport)
    assert_not_connected_invariants(driver)  # starting state remains unchanged


# Query methods - invalid starting state(SCANNING)
@pytest.mark.parametrize(
    "operation",
    [
        lambda driver: driver.get_info(),
        lambda driver: driver.get_health(),
        lambda driver: driver.get_samplerate(),
        lambda driver: driver.reset(),
        lambda driver: driver._check_health(),
    ],
)
def test_query_methods_raise_invalid_state_error_when_scanning(
    operation,
    scanning_driver,
):
    driver, transport = scanning_driver

    with pytest.raises(RPLidarStateError, match="Operation requires working state"):
        operation(driver)

    assert_transport_untouched(transport)
    assert_scanning_invariants(driver)  # starting state remains unchanged


# Query methods - invalid starting state(IDLE)
@pytest.mark.parametrize(
    "operation",
    [lambda driver: driver.stop(), lambda driver: driver.reset()],
)
def test_stop_and_reset_raise_invalid_state_error_in_idle(operation, idle_driver):
    driver, transport = idle_driver

    with pytest.raises(RPLidarStateError, match="Operation requires working state"):
        operation(driver)

    assert_transport_untouched(transport)
    assert_idle_invariants(driver)  # starting state remains unchanged

# Query methods - invalid starting state(PROTECTION_STOP)
def test_stop_and_raise_invalid_state_error_in_protection_stop(protection_stop_driver):
    driver, transport = protection_stop_driver

    with pytest.raises(RPLidarStateError, match="Operation requires working state"):
        driver.stop()

    assert_transport_untouched(transport)
    assert_protection_stop_invariants(driver)  # starting state remains unchanged

# ---------------------------------------Timeout failures----------------------------------------#


# query methods with required idle start state - timeout error during read
@pytest.mark.parametrize(
    "operation, command",
    [
        (lambda driver: driver.get_info(), RPLidarCommand.GET_INFO.value),
        (lambda driver: driver.get_health(), RPLidarCommand.GET_HEALTH.value),
        (lambda driver: driver.get_samplerate(), RPLidarCommand.GET_SAMPLERATE.value),
        (lambda driver: driver._check_health(), RPLidarCommand.GET_HEALTH.value),
    ],
)
def test_query_methods_read_timeout_restores_idle(operation, command, idle_driver):
    driver, transport = idle_driver

    transport.fail_read = TransportTimeoutError("timeout read")

    with pytest.raises(RPLidarTimeoutError, match="timeout read") as exc_info:
        operation(driver)

    assert isinstance(exc_info.value.__cause__, TransportTimeoutError)
    assert transport.written == bytes([0xA5, command])

    assert_idle_invariants(driver)


# query methods with required protection_stop start state - timeout error during read
@pytest.mark.parametrize(
    "opeartion, command",
    [
        (lambda driver: driver.get_info(), RPLidarCommand.GET_INFO.value),
        (lambda driver: driver.get_health(), RPLidarCommand.GET_HEALTH.value),
        (lambda driver: driver.get_samplerate(), RPLidarCommand.GET_SAMPLERATE.value),
        (lambda driver: driver._check_health(), RPLidarCommand.GET_HEALTH.value),
    ],
)
def test_query_methods_read_timeout_restores_protection_stop(
    opeartion, command, protection_stop_driver
):
    driver, transport = protection_stop_driver

    transport.fail_read = TransportTimeoutError("timeout read")

    with pytest.raises(RPLidarTimeoutError, match="timeout read") as exc_info:
        opeartion(driver)

    assert isinstance(exc_info.value.__cause__, TransportTimeoutError)
    assert transport.written == bytes([0xA5, command])

    assert_protection_stop_invariants(driver)


def test_reset_read_timeout_restores_protection_stop(protection_stop_driver):
    driver, transport = protection_stop_driver

    transport.fail_read = TransportTimeoutError("timeout read")

    with pytest.raises(RPLidarTimeoutError, match="timeout read") as exc_info:
        driver.reset()

    assert isinstance(exc_info.value.__cause__, TransportTimeoutError)
    assert transport.written == bytes(
        [0xA5, RPLidarCommand.RESET.value, 0xA5, RPLidarCommand.GET_HEALTH.value]
    )
    assert_protection_stop_invariants(driver)


# query methods with required idle start state - timeout error while writing request
@pytest.mark.parametrize(
    "operation",
    [
        lambda driver: driver.get_info(),
        lambda driver: driver.get_health(),
        lambda driver: driver.get_samplerate(),
        lambda driver: driver._check_health(),
    ],
)
def test_query_methods_write_timeout_restores_idle_(operation, idle_driver):
    driver, transport = idle_driver

    transport.fail_write = TransportTimeoutError("write timed out")

    with pytest.raises(RPLidarTimeoutError, match="write timed out") as exc_info:
        operation(driver)

    assert isinstance(exc_info.value.__cause__, TransportTimeoutError)
    assert_transport_synced(transport)
    assert_idle_invariants(driver)


# query methods with required protection_stop start state - timeout error while writing request
@pytest.mark.parametrize(
    "operation",
    [
        lambda driver: driver.get_info(),
        lambda driver: driver.get_health(),
        lambda driver: driver.get_samplerate(),
        lambda driver: driver.reset(),
        lambda driver: driver._check_health(),
    ],
)
def test_query_methods_write_timeout_restores_protection_stop(operation, protection_stop_driver):
    driver, transport = protection_stop_driver

    transport.fail_write = TransportTimeoutError("write timed out")

    with pytest.raises(RPLidarTimeoutError, match="write timed out") as exc_info:
        operation(driver)

    assert isinstance(exc_info.value.__cause__, TransportTimeoutError)
    assert_transport_synced(transport)
    assert_protection_stop_invariants(driver)


## query methods with required scanning start state - timeout error while writing request
def test_stop_write_timeout_restore_scanning_state(scanning_driver):
    driver, transport = scanning_driver

    transport.fail_write = TransportTimeoutError("write timed out")

    with pytest.raises(RPLidarTimeoutError, match="write timed out") as exc_info:
        driver.stop()

    assert isinstance(exc_info.value.__cause__, TransportTimeoutError)
    assert_scanning_invariants(driver) # starting state remains unchanged
    assert_transport_synced(transport)



# --------------------------------------Connection failures---------------------------------------#


## Query in idle driver - TransportConnectionError while sending request
@pytest.mark.parametrize(
    "operation",
    [
        lambda driver: driver.get_info(),
        lambda driver: driver.get_health(),
        lambda driver: driver.get_samplerate(),
        lambda driver: driver._check_health(),
    ],
)
def test_in_idle_query_write_connection_failure_transitions_to_not_connected(
    operation,
    idle_driver,
):
    driver, transport = idle_driver

    transport.fail_write = TransportConnectionError("failed write")

    with pytest.raises(RPLidarConnectionError, match="failed write") as exc_info:
        operation(driver)

    assert isinstance(exc_info.value.__cause__, TransportConnectionError)
    assert_transport_closed_in_connection_error(transport)
    assert_transport_did_not_sync_in_connection_error(transport)
    assert_not_connected_invariants(driver) # state transitions to NOT_CONNECTED


## Query in protection stop driver - TransportConnectionError while sending request
@pytest.mark.parametrize(
    "operation",
    [
        lambda driver: driver.get_info(),
        lambda driver: driver.get_health(),
        lambda driver: driver.get_samplerate(),
        lambda driver: driver.reset(),
        lambda driver: driver._check_health(),
    ],
)
def test_in_protection_stop_query_connection_failure_shifts_to_not_connected(
    operation,
    protection_stop_driver,
):
    driver, transport = protection_stop_driver

    transport.fail_write = TransportConnectionError("failed write")

    with pytest.raises(RPLidarConnectionError, match="failed write") as exc_info:
        operation(driver)

    assert isinstance(exc_info.value.__cause__, TransportConnectionError)
    assert_transport_closed_in_connection_error(transport)
    assert_transport_did_not_sync_in_connection_error(transport)
    assert_not_connected_invariants(driver) # state transitions to NOT_CONNECTED


## Query in scanning driver - TransportConnectionError while sending request
def test_in_scanning_query_connection_failure_shifts_to_not_connected(
    scanning_driver,
):
    driver, transport = scanning_driver

    transport.fail_write = TransportConnectionError("failed write")

    with pytest.raises(RPLidarConnectionError, match="failed write") as exc_info:
        driver.stop()

    assert isinstance(exc_info.value.__cause__, TransportConnectionError)
    assert_transport_closed_in_connection_error(transport)
    assert_transport_did_not_sync_in_connection_error(transport)
    assert_not_connected_invariants(driver) # state transitions to NOT_CONNECTED


## Query in idle driver - TransportConnectionError while reading response
@pytest.mark.parametrize(
    "operation",
    [
        lambda driver: driver.get_info(),
        lambda driver: driver.get_health(),
        lambda driver: driver.get_samplerate(),
        lambda driver: driver._check_health(),
    ],
)
def test_in_idle_query_read_connection_failure_transitions_to_not_connected(
    operation,
    idle_driver,
):
    driver, transport = idle_driver

    transport.fail_read = TransportConnectionError("failed read")

    with pytest.raises(RPLidarConnectionError, match="failed read") as exc_info:
        operation(driver)

    assert isinstance(exc_info.value.__cause__, TransportConnectionError)
    assert_transport_closed_in_connection_error(transport)
    assert_transport_did_not_sync_in_connection_error(transport)
    assert_not_connected_invariants(driver) # state transitions to NOT_CONNECTED


## Query in protection stop driver - TransportConnectionError while reading response
@pytest.mark.parametrize(
    "operation, command",
    [
        (lambda driver: driver.get_info(), RPLidarCommand.GET_INFO.value),
        (lambda driver: driver.get_health(), RPLidarCommand.GET_HEALTH.value),
        (lambda driver: driver.get_samplerate(), RPLidarCommand.GET_SAMPLERATE.value),
        (lambda driver: driver._check_health(), RPLidarCommand.GET_HEALTH.value),
    ],
)
def test_in_protection_stop_query_read_connection_failure_shifts_to_not_connected(
    operation,
    command,
    protection_stop_driver,
):
    driver, transport = protection_stop_driver

    transport.fail_read = TransportConnectionError("failed read")

    with pytest.raises(RPLidarConnectionError, match="failed read") as exc_info:
        operation(driver)

    assert transport.written == bytes([0xA5, command])
    assert isinstance(exc_info.value.__cause__, TransportConnectionError)
    assert_transport_closed_in_connection_error(transport)
    assert_transport_did_not_sync_in_connection_error(transport)
    assert_not_connected_invariants(driver) # state transitions to NOT_CONNECTED


### driver.reset() - TransportConnectionError while reading response
def test_in_protection_stop_reset_read_connection_failure_shifts_to_not_connected(
    protection_stop_driver,
):
    driver, transport = protection_stop_driver

    transport.fail_read = TransportConnectionError("failed read")

    with pytest.raises(RPLidarConnectionError, match="failed read") as exc_info:
        driver.reset()

    assert transport.written == bytes(
        [0xA5, RPLidarCommand.RESET.value, 0xA5, RPLidarCommand.GET_HEALTH.value]
    )
    assert isinstance(exc_info.value.__cause__, TransportConnectionError)
    print(transport.flush_count)
    assert_transport_closed_in_connection_error(transport)
    assert_transport_synced(transport)
    assert_not_connected_invariants(driver) # state transitions to NOT_CONNECTED
