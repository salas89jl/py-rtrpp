from rtrpp.sensors.rplidar.driver import RPLidarDriver
from tests.sensors.rplidar.driver.conftest import FakeTransport

from rtrpp.sensors.rplidar.protocol import (
    RPLidarWorkingState,
    RPLidarScanningMode,
    RPLidarResponseType,
    RPLidarCommand,
)


def assert_not_connected_invariants(
    driver: RPLidarDriver,
) -> None:
    assert driver._working_state is RPLidarWorkingState.NOT_CONNECTED
    assert driver._scanning_state.is_active is False
    assert driver._scanning_state.mode is RPLidarScanningMode.INACTIVE
    assert driver._scanning_state.response_type is None
    assert driver._scanning_state.packet_size == 0
    assert driver._scanning_state.completed_scan_count == 0
    assert driver._pending_measurement is None


def assert_idle_invariants(
    driver: RPLidarDriver,
) -> None:
    assert driver._working_state is RPLidarWorkingState.IDLE
    assert driver._scanning_state.is_active is False
    assert driver._scanning_state.mode is RPLidarScanningMode.INACTIVE
    assert driver._scanning_state.response_type is None
    assert driver._scanning_state.packet_size == 0
    assert driver._scanning_state.completed_scan_count == 0
    assert driver._pending_measurement is None


def assert_protection_stop_invariants(
    driver: RPLidarDriver,
) -> None:
    assert driver._working_state is RPLidarWorkingState.PROTECTION_STOP
    assert driver._scanning_state.is_active is False
    assert driver._scanning_state.mode is RPLidarScanningMode.INACTIVE
    assert driver._scanning_state.response_type is None
    assert driver._scanning_state.packet_size == 0
    assert driver._scanning_state.completed_scan_count == 0
    assert driver._pending_measurement is None


def assert_scanning_invariants(
    driver: RPLidarDriver,
) -> None:
    assert driver._working_state is RPLidarWorkingState.SCANNING
    assert driver._scanning_state.is_active is True
    assert driver._scanning_state.mode is RPLidarScanningMode.STANDARD
    assert driver._scanning_state.response_type is RPLidarResponseType.MEASUREMENT_DATA
    assert driver._scanning_state.packet_size == 5
    assert driver._scanning_state.completed_scan_count >= 0

    pending = driver._pending_measurement
    assert pending is None or pending.start_flag is True


def assert_state_invariants(
    driver: RPLidarDriver,
    driver_state: str,
) -> None:
    if driver_state == "not_connected_driver":
        assert_not_connected_invariants(driver)
    elif driver_state == "idle_driver":
        assert_idle_invariants(driver)
    elif driver_state == "scanning_driver":
        assert_scanning_invariants(driver)
    else:
        assert_protection_stop_invariants(driver)


def assert_transport_untouched(
    transport: FakeTransport,
) -> None:
    assert transport.open_count == 0
    assert transport.close_count == 0
    assert transport.written == b""


def assert_transport_synced(
    transport: FakeTransport,
) -> None:
    assert transport.flush_count == 1
    assert transport.reset_input_count == 1
    assert transport.reset_output_count == 1


def assert_transport_closed_in_connection_error(
    transport: FakeTransport,
) -> None:
    assert transport.is_open is False
    assert transport.close_count == 1
    assert transport.internal_buffer == b""


def assert_transport_did_not_sync_in_connection_error(
    transport: FakeTransport,
) -> None:
    assert transport.flush_count == 0
    assert transport.reset_input_count == 0
    assert transport.reset_output_count == 0


def assert_stream_error_recovery_restores_idle(
    driver: RPLidarDriver,
    transport: FakeTransport,
) -> None:
    # Idle state invariants
    assert_idle_invariants(driver)
 
    assert_transport_synced(transport)

def assert_connection_error_recovery_restores_not_connected_driver(
        driver: RPLidarDriver,
        transport: FakeTransport,
) -> None:
    assert_not_connected_invariants(driver)
    assert_transport_closed_in_connection_error(transport)
    assert_transport_did_not_sync_in_connection_error(transport)