import pytest

from rtrpp.sensors.rplidar.protocol import (
    RPLidarCommand,
    RPLidarScanData,
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

from rtrpp.sensors.rplidar.rplidar_warnings import (
    RPLidarHealthWarning,
)

from tests.sensors.rplidar.test_support.fakes import (
    queue_get_health_response,
)

from tests.sensors.rplidar.driver.assertions import (
    assert_not_connected_invariants,
    assert_idle_invariants,
    assert_protection_stop_invariants,
    assert_transport_untouched,
)


# connect - successful outcomes
def test_connect_good_health_enters_idle(not_connected_driver):
    driver, transport = not_connected_driver

    queue_get_health_response(
        transport=transport,
        status=0,  # GOOD
        error_code=0,  # No error
    )

    driver.connect()

    assert_idle_invariants(driver)
    assert transport.written == bytes([0xA5, RPLidarCommand.GET_HEALTH.value])


def test_connect_warning_health_enters_idle_and_warns(not_connected_driver):
    driver, transport = not_connected_driver

    queue_get_health_response(
        transport,
        status=1,
        error_code=0x1234,
    )

    with pytest.warns(RPLidarHealthWarning, match="potential risk"):
        driver.connect()

    assert_idle_invariants(driver)
    assert driver._health.status == 1
    assert driver._health.error_code == 0x1234


def test_connect_error_health_enters_protection_stop(not_connected_driver):
    driver, transport = not_connected_driver

    queue_get_health_response(
        transport,
        status=2,
        error_code=0x1234,
    )

    with pytest.raises(RPLidarDeviceError, match="internal error"):
        driver.connect()

    assert transport.is_open is True
    assert_protection_stop_invariants(driver)
    assert driver._health.status == 2
    assert driver._health.error_code == 0x1234


# connect - invalid state
def test_connect_raises_state_error_with_invalid_starting_state(idle_driver):
    driver, transport = idle_driver

    with pytest.raises(
        RPLidarStateError,
        match="Operation requires working state NOT_CONNECTED; current working state is IDLE.",
    ):
        driver.connect()

    assert_idle_invariants(driver)
    assert_transport_untouched(transport)


# connect - initialization failures
def test_connect_open_failure_restores_not_connected(
    not_connected_driver,
):
    driver, transport = not_connected_driver

    transport.fail_open = TransportConnectionError("Failed open")

    with pytest.raises(RPLidarConnectionError, match="open"):
        driver.connect()

    assert_not_connected_invariants(driver)
    assert transport.is_open is False


def test_connect_health_timeout_restores_not_connected(
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
    assert transport.is_open is False
    assert driver._health.status == 0


def test_connect_health_timeout_while_resquesting_restores_not_connected(
    not_connected_driver,
):
    driver, transport = not_connected_driver

    transport.fail_write = TransportTimeoutError("Timeout requesting health")

    with pytest.raises(RPLidarTimeoutError, match="Timeout requesting health"):
        driver.connect()

    assert_not_connected_invariants(driver)
    assert transport.is_open is False
    assert driver._health.status == 0
    assert driver._health.error_code == 0


def test_connect_health_protocol_error_restores_not_connected(
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


def test_connect_health_connection_error_restores_not_connected(
    not_connected_driver,
):
    driver, transport = not_connected_driver

    transport.fail_write = TransportConnectionError("Failed requesting health")
    with pytest.raises(RPLidarConnectionError, match="requesting health"):
        driver.connect()

    assert_not_connected_invariants(driver)


def test_connect_raises_state_error_with_repeated_connects(
    not_connected_driver,
):
    driver, transport = not_connected_driver

    queue_get_health_response(transport, status=0, error_code=0x1234)

    driver.connect()

    with pytest.raises(RPLidarStateError, match="requires working state NOT_CONNECTED"):
        driver.connect()

    assert_idle_invariants(driver)
    assert transport.open_count == 1


# connect - recovery failures
def test_connect_health_failure_restores_not_connected(
    not_connected_driver,
):
    driver, transport = not_connected_driver

    transport.fail_write = TransportTimeoutError("Timeout requesting health")
    transport.fail_flush = TransportConnectionError("Failed flush")

    with pytest.raises(RPLidarConnectionError) as exc_info:
        driver.connect()

    assert "Failed flush" in str(exc_info.value)
    assert_not_connected_invariants(driver)


# disconnect - starting states
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


def test_disconnect_closes_from_scanning_state(scanning_driver):
    driver, transport = scanning_driver

    driver.disconnect()

    assert transport.close_count == 1
    assert transport.written == bytes([0xA5, RPLidarCommand.STOP.value])
    assert_not_connected_invariants(driver)


def test_disconnect_closes_from_protection_stop(protection_stop_driver):
    driver, transport = protection_stop_driver

    driver.disconnect()

    assert_not_connected_invariants(driver)
    assert transport.close_count == 1


def test_disconnect_closes_with_repeated_disconnects(
    scanning_driver,
):
    driver, transport = scanning_driver

    driver.disconnect()
    driver.disconnect()

    assert_not_connected_invariants(driver)
    assert transport.written == bytes([0xA5, RPLidarCommand.STOP.value])
    assert transport.close_count == 2


# disconnect - cleanup failures and precedence
def test_disconnect_closes_when_best_effort_stop_fails(scanning_driver):
    driver, transport = scanning_driver

    transport.fail_write = TransportConnectionError("STOP failed")

    with pytest.raises(RPLidarConnectionError, match="STOP"):
        driver.disconnect()

    assert_not_connected_invariants(driver)
    assert transport.is_open is False
    assert transport.close_count == 1


def test_disconnect_closes_when_best_effort_stop_timesout(scanning_driver):
    driver, transport = scanning_driver

    transport.fail_write = TransportTimeoutError("STOP timed out")

    with pytest.raises(RPLidarTimeoutError, match="STOP timed out"):
        driver.disconnect()

    assert_not_connected_invariants(driver)


def test_disconnect_close_failure_restores_logical_state_from_scanning(scanning_driver):

    measurement = RPLidarScanData(
        start_flag=True,
        quality=1,
        angle_degrees=90.0,
        distance_mm=10.0,
    )
    driver, transport = scanning_driver

    driver._pending_measurement = measurement

    transport.fail_close = TransportConnectionError("Close failed")

    with pytest.raises(RPLidarConnectionError, match="Close failed"):
        driver.disconnect()

    assert_not_connected_invariants(driver)


def test_disconnect_close_failure_restores_logical_state(idle_driver):
    driver, transport = idle_driver

    transport.fail_close = TransportConnectionError("close failed")

    with pytest.raises(RPLidarConnectionError, match="close"):
        driver.disconnect()

    assert_not_connected_invariants(driver)
    assert transport.close_count == 1


def test_disconnect_close_failure_takes_precedence(
    scanning_driver,
):
    driver, transport = scanning_driver

    transport.fail_write = TransportConnectionError("STOP failed")
    transport.fail_close = TransportConnectionError("close failed")

    with pytest.raises(RPLidarConnectionError, match="close failed"):
        driver.disconnect()

    assert_not_connected_invariants(driver)
    assert transport.close_count == 1
