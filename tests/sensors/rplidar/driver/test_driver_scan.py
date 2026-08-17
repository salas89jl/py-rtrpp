import pytest

from rtrpp.sensors.rplidar.exceptions import (
    RPLidarConnectionError,
    RPLidarProtocolError,
    RPLidarStateError,
    RPLidarTimeoutError,
    TransportConnectionError,
    TransportTimeoutError,
)
from rtrpp.sensors.rplidar.protocol import (
    RPLidarCommand,
)
from tests.sensors.rplidar.driver.assertions import (
    assert_scanning_invariants,
    assert_state_invariants,
    assert_stream_error_recovery_restores_idle,
    assert_connection_error_recovery_restores_not_connected_driver,
    assert_transport_untouched,
)
from tests.sensors.rplidar.test_support.fakes import (
    queue_response_descriptor,
    queue_multiple_scan_data_responses,

)

# ---------------------------------------Test start_scan()----------------------------------------#


## Test successful outcomes - Ensure Driver enters and satisfies SCANNING invariants
def test_start_scan_enters_scanning_state_with_valid_request_and_response_descriptor(idle_driver):
    driver, transport = idle_driver

    queue_response_descriptor(transport, response_descriptor=b"\xa5\x5a\x05\x00\x00\x40\x81")

    driver.start_scan()

    assert transport.written == bytes([0xA5, RPLidarCommand.SCAN.value])
    assert_scanning_invariants(driver)


## Test state failures - No change in starting state
@pytest.mark.parametrize(
    "driver_state", ["not_connected_driver", "scanning_driver", "protection_stop_driver"]
)
def test_start_scan_raises_state_error_when_scanning(driver_state, request):
    driver, transport = request.getfixturevalue(driver_state)
    print(driver_state)

    with pytest.raises(RPLidarStateError, match="Operation requires working state"):
        driver.start_scan()

    assert_transport_untouched(transport)
    assert_state_invariants(driver, driver_state)


## Test protocol failures - Ensure stream recovery is applied and driver statisfies IDLE invariants
def test_start_scan_reads_invalid_start_flags(idle_driver):
    driver, transport = idle_driver

    queue_response_descriptor(transport, response_descriptor=b"\x00\x00\x05\x00\x00\x40\x81")

    with pytest.raises(
        RPLidarProtocolError, match="Invalid response descriptor start flags"
    ) as exc_info:
        driver.start_scan()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_stream_error_recovery_restores_idle(driver, transport)


def test_start_scan_reads_invalid_descriptor_response_length(idle_driver):
    driver, transport = idle_driver

    queue_response_descriptor(transport, response_descriptor=b"\xa5\x5a\x02\x00\x00\x40\x81")
    with pytest.raises(
        RPLidarProtocolError, match="expected 5 response bytes, received descriptor length 2."
    ) as exc_info:
        driver.start_scan()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_stream_error_recovery_restores_idle(driver, transport)


def test_start_scan_reads_invalid_descriptor_send_mode(idle_driver):
    driver, transport = idle_driver

    queue_response_descriptor(transport, response_descriptor=b"\xa5\x5a\x05\x00\x00\x00\x81")

    with pytest.raises(RPLidarProtocolError, match="expected send mode 1, but got 0") as exc_info:
        driver.start_scan()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_stream_error_recovery_restores_idle(driver, transport)


def test_start_scan_reads_invalid_descriptor_data_type(idle_driver):
    driver, transport = idle_driver

    queue_response_descriptor(transport, response_descriptor=b"\xa5\x5a\x05\x00\x00\x40\x82")

    with pytest.raises(
        RPLidarProtocolError, match="expected data type 129, but got 130"
    ) as exc_info:
        driver.start_scan()

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert_stream_error_recovery_restores_idle(driver, transport)


## Test connection failures - Ensure connection error recovery performed and moves to NOT_CONNECTED


def test_start_scan_write_connection_failure_restores_not_connected_driver(idle_driver):
    driver, transport = idle_driver

    transport.fail_write = TransportConnectionError("failed write")

    with pytest.raises(RPLidarConnectionError, match="failed write") as exc_info:
        driver.start_scan()

    assert isinstance(exc_info.value.__cause__, TransportConnectionError)
    assert_connection_error_recovery_restores_not_connected_driver(driver, transport)


def test_start_scan_read_connection_failure_restores_not_connected_driver(idle_driver):
    driver, transport = idle_driver

    transport.fail_read = TransportConnectionError("failed read")

    with pytest.raises(RPLidarConnectionError, match="failed read") as exc_info:
        driver.start_scan()

    assert isinstance(exc_info.value.__cause__, TransportConnectionError)
    assert_connection_error_recovery_restores_not_connected_driver(driver, transport)


## Test timeout failures - Ensure stream recoery is applied and driver satisfies IDLE invariants

def test_start_scan_write_timeout_restores_idle_driver(idle_driver):
    driver, transport = idle_driver

    transport.fail_write = TransportTimeoutError("write timeout")

    with pytest.raises(RPLidarTimeoutError, match="write timeout") as exc_info:
        driver.start_scan()

    assert isinstance(exc_info.value.__cause__, TransportTimeoutError)
    assert_stream_error_recovery_restores_idle(driver, transport)



#-----------------------------------------Test read_scan()-----------------------------------#

## Test successful outcomes 
### - Ensure Driver remains in SCANNING state and satisfies SCANNING invariants
def test_read_scan_returns_valid_measurement_packet_and_satisfies_scanning_invariants(scanning_driver):
    driver, transport = scanning_driver

    
    queue_multiple_scan_data_responses(
        transport,
        num_responses=3,
        _start_flag=b"\x02",
        angle_increment=60.0,
        distance_mm=10.0
    )

    queue_multiple_scan_data_responses(
        transport,
        num_responses=5,
        _start_flag=b"\x01",
        angle_increment=10.0,
        distance_mm=10.0
    )

    scan = driver.read_scan()

    assert scan[0].start_flag is True
    assert len(scan) == 5
    assert scan[0].angle_degrees == 0.0
    assert scan[1].angle_degrees == 10.0
    assert scan[2].angle_degrees == 20.0
    assert scan[3].angle_degrees == 30.0
    assert scan[4].angle_degrees == 40.0
    assert_scanning_invariants(driver)

def test_read_scan_with_valid(scanning_driver):
    driver, transport = scanning_driver

    responses = [
        b"\xa6\x01\x00\x00\x00",  # Start Flag=0
        b"\xa6\x01\x00\x00\x00",  # Start Flag=0
        b"\xa6\x01\x00\x00\x00",  # Start Flag=0
        b"\xa5\x95\x12\xc8\x03",  # Boundary measurement (start of next scan)
        b"\x96\x01\xb2\xff\xff",
        b"\xa6\x01\x00\x00\x00", 
        b"\xa6\x2b\x15\xb1\xa2",
        b"\xa5\x01\x00\x00\x00",
    ]   

    for i in range(len(responses)):

        transport.responses.append(responses[i])

    scan = driver.read_scan()
    print(len(scan))
    assert scan[1].start_flag is False
    assert scan[1].quality == 37
    assert scan[1].angle_degrees == pytest.approx(356.0)
    assert scan[1].distance_mm == pytest.approx(16383.75)

### - Ensure Driver returns a valid measurement packet and complete scan revolution
### - Ensure Driver returns scan rotation that starts with a start flag and ends with a stop flag
### - Ensure Driver pending boundary is stored exactly once and returned in the next read_scan() call
### - Ensure no measurement packets are lost or duplicated in the stream of packets returned by read_scan() calls
### - 