from rtrpp.sensors.rplidar.driver import RPLidarDriver
from tests.sensors.rplidar.driver.conftest import FakeTransport

from rtrpp.sensors.rplidar.protocol import (
    RPLidarWorkingState,
    RPLidarScanningMode,
    RPLidarResponseType,
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
    assert driver._scanning_state.mode is RPLidarScanningMode.STANDARD_SCAN
    assert driver._scanning_state.response_type is RPLidarResponseType.MEASUREMENT_DATA
    assert driver._scanning_state.packet_size == 5
    assert driver._scanning_state.completed_scan_count >= 0

    pending = driver._pending_measurement
    assert pending is None or pending.start_flag is True


def assert_transport_untouched(
    transport: FakeTransport,
):
    assert transport.open_count == 0
    assert transport.close_count == 0
    assert transport.written == b""
