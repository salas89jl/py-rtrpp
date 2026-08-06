import pytest

from tests.sensors.rplidar.test_support.fakes import FakeTransport
from src.rtrpp.sensors.rplidar.driver import RPLidarDriver
from src.rtrpp.sensors.rplidar.protocol import (
    RPLidarWorkingState,
    RPLidarScanningMode,
    RPLidarResponseType,
)


@pytest.fixture
def not_connected_driver():
    transport = FakeTransport()
    driver = RPLidarDriver(transport)
    return driver, transport


@pytest.fixture
def idle_driver():
    transport = FakeTransport(is_open=True)
    driver = RPLidarDriver(transport)

    driver._working_state = RPLidarWorkingState.IDLE
    driver._clear_scanning_state()

    return driver, transport


@pytest.fixture
def scanning_driver():
    transport = FakeTransport(is_open=True)
    driver = RPLidarDriver(transport)

    driver._working_state = RPLidarWorkingState.SCANNING
    driver._update_scanning_state(
        packet_size=5,
        mode=RPLidarScanningMode.STANDARD,
        response_type=RPLidarResponseType.MEASUREMENT_DATA,
        completed_scan_count=0,
    )

    return driver, transport


@pytest.fixture
def protection_stop_driver():
    transport = FakeTransport()
    driver = RPLidarDriver(transport)

    driver._working_state = RPLidarWorkingState.PROTECTION_STOP
    driver._clear_scanning_state()

    return driver, transport
