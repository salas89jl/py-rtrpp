import pytest

from rtrpp.sensors.rplidar.protocol import (
    RPLidarCommand,
)

from src.rtrpp.sensors.rplidar.exceptions import (
    TransportConnectionError,
    TransportTimeoutError,
    RPLidarStateError,
    RPLidarConnectionError,
    RPLidarTimeoutError,
    RPLidarDeviceError,
    RPLidarProtocolError,
)

from src.rtrpp.sensors.rplidar.rplidar_warnings import (
    RPLidarHealthWarning,
)

from tests.sensors.rplidar.test_support.fakes import (
    queue_get_health_response,
)

from tests.sensors.rplidar.driver.assertions import (
    assert_not_connected_invariants,
    assert_idle_invariants,
    assert_protection_stop_invariants,
)


# Tests for driver.connect()
def test_connect_valid_transition_to_idle_state(not_connected_driver):
    driver, transport = not_connected_driver

    queue_get_health_response(
        transport=transport,
        status=0,  # GOOD
        error_code=0,  # No error
    )

    driver.connect()

    assert_idle_invariants(driver)
    assert transport.written == bytes([0xA5, RPLidarCommand.GET_HEALTH.value])


def test_connect_raises_state_error_with_invalid_starting_state(idle_driver):
    driver, transport = idle_driver

    with pytest.raises(
        RPLidarStateError,
        match="Operation requires working state NOT_CONNECTED; current working state is IDLE.",
    ):
        driver.connect()

    assert_idle_invariants(driver)


def test_connect_emmits_warning_for_health_warning(not_connected_driver):
    driver, transport = not_connected_driver

    queue_get_health_response(
        transport,
        status=1,
        error_code=0x1234,
    )

    with pytest.warns(RPLidarHealthWarning):
        driver.connect()

    assert_idle_invariants(driver)
    assert driver._health.status == 1
    assert driver._health.error_code == 0x1234


def test_connect_raises_health_error_and_moves_to_protection_stop(not_connected_driver):
    driver, transport = not_connected_driver

    queue_get_health_response(
        transport,
        status=2,
        error_code=0x1234,
    )

    with pytest.raises(RPLidarDeviceError, match="internal error"):
        driver.connect()

    assert_protection_stop_invariants(driver)
    assert driver._health.status == 2
    assert driver._health.error_code == 0x1234


def test_connect_stays_in_not_connected_state_with_open_error(
    not_connected_driver,
):
    driver, transport = not_connected_driver

    transport.fail_open = TransportConnectionError("Failed open")

    with pytest.raises(RPLidarConnectionError, match="open"):
        driver.connect()

    assert_not_connected_invariants(driver)
    assert transport.is_open is False


def test_connect_stays_in_not_connected_state_with_health_value_error(
    not_connected_driver,
):
    driver, transport = not_connected_driver

    queue_get_health_response(
        transport,
        status=3,
        error_code=0x1234,
    )

    with pytest.raises(RPLidarProtocolError, match="Invalid GET_HEALTH status"):
        driver.connect()

    assert_not_connected_invariants(driver)
    assert driver._health.status == 0
    assert driver._health.error_code == 0


def test_connect_stays_in_not_connected_state_with_health_timeout_error(
    not_connected_driver,
):
    driver, transport = not_connected_driver

    queue_get_health_response(
        transport,
        status=0,
        error_code=0x1234,
    )

    transport.fail_read = TransportTimeoutError("Timeout requesting health check")

    with pytest.raises(RPLidarTimeoutError, match="health check"):
        driver.connect()

    assert_not_connected_invariants(driver)
    assert driver._health.status == 0
    assert driver._health.error_code == 0


def test_connect_stays_in_not_connected_state_with_write_connection_error(
    not_connected_driver,
):
    driver, transport = not_connected_driver

    transport.fail_write = TransportConnectionError("Failed requesting health")
    with pytest.raises(RPLidarConnectionError, match="requesting health"):
        driver.connect()

    assert_not_connected_invariants(driver)


def test_connect_stays_in_not_connnected_state_with_write_timeout_error(
    not_connected_driver,
):
    driver, transport = not_connected_driver

    transport.fail_write = TransportTimeoutError("Timeout requesting health")

    with pytest.raises(RPLidarTimeoutError, match="Timeout requesting health"):
        driver.connect()

    assert_not_connected_invariants(driver)
    assert driver._health.status == 0
    assert driver._health.status == 0


def test_connect_stays_in_connected_state_with_flush_error(
    not_connected_driver,
):
    driver, transport = not_connected_driver

    transport.fail_write = TransportTimeoutError("Timeout requesting health")
    transport.fail_flush = TransportConnectionError("Failed flush")

    with pytest.raises(RPLidarConnectionError) as exc_info:
        driver.connect()

    assert "Failed flush" in str(exc_info.value)
    assert_not_connected_invariants(driver)


# Tests for driver.disconnect()


def test_disconnect_closes_from_not_connected_state(not_connected_driver):
    driver, transport = not_connected_driver

    driver.disconnect()

    assert_not_connected_invariants(driver)
    assert transport.close_count == 1


def test_disconnect_closes_from_idle_state(idle_driver):
    driver, transport = idle_driver

    driver.disconnect()

    assert_not_connected_invariants(driver)
    assert transport.close_count == 1


def test_disconnect_closes_scanning_state(scanning_driver):
    driver, transport = scanning_driver

    driver.disconnect()

    assert_not_connected_invariants(driver)
    assert transport.close_count == 1
    assert transport.written == bytes([0xA5, RPLidarCommand.STOP.value])


def test_disconnect_closes_from_protection_stop(protection_stop_driver):
    driver, transport = protection_stop_driver

    driver.disconnect()

    assert_not_connected_invariants(driver)
    assert transport.close_count == 1


def test_disconnect_closes_with_stop_error(scanning_driver):
    driver, transport = scanning_driver

    transport.fail_write = TransportConnectionError("STOP failed")

    with pytest.raises(RPLidarConnectionError, match="STOP"):
        driver.disconnect()

    assert_not_connected_invariants(driver)
    assert transport.is_open is False
    assert transport.close_count == 2


def test_disconnect_transitions_not_connected_state_with_close_error(idle_driver):
    driver, transport = idle_driver

    transport.fail_close = TransportConnectionError("close failed")

    with pytest.raises(RPLidarConnectionError, match="close"):
        driver.disconnect()

    assert_not_connected_invariants(driver)
    assert transport.close_count == 2


def test_disconnect_close_takes_precedence_over_stop_error(
    scanning_driver,
):
    driver, transport = scanning_driver

    transport.fail_write = TransportConnectionError("STOP failed")
    transport.fail_close = TransportConnectionError("close failed")

    with pytest.raises(RPLidarConnectionError, match="close failed"):
        driver.disconnect()

    assert_not_connected_invariants(driver)
    assert transport.close_count == 3
