import pytest

from rtrpp.sensors.rplidar.protocol import (
    RPLidarCommand,
    build_request,
    parse_response_descriptor,
    parse_scan_data,
    parse_get_info_response,
    parse_get_health_response,
    parse_get_samplerate_response,
)

# Parse build request test(s)
def test_build_request_without_payload():
    packet = build_request(RPLidarCommand.GET_INFO)

    assert packet == b"\xA5\x50"

def test_build_request_with_payload():
    payload =  b"\x00\x00\x00\x00\x00"

    packet = build_request(RPLidarCommand.EXPRESS_SCAN,payload)

    assert packet == b"\xA5\x82\x05\x00\x00\x00\x00\x00\x22"

def test_build_request_invalid_command():
    with pytest.raises(ValueError):
        build_request(0x22)   

def test_build_request_accepts_255_byte_payload():
    payload = bytes(range(255))
    
    packet = build_request(RPLidarCommand.EXPRESS_SCAN, payload)

    assert packet[2] == 255

def test_build_request_rejects_256_byte_payload():
    payload = bytes(range(256))
    with pytest.raises(ValueError):
        build_request(RPLidarCommand.EXPRESS_SCAN, payload)

def test_build_request_computes_checksum():
    payload = b"\x01\x02\x03"

    packet = build_request(RPLidarCommand.EXPRESS_SCAN, payload)

    expected_checksum = 0xA5 ^ 0x82 ^ 0x03 ^ 0x01 ^ 0x02 ^ 0x03
    assert packet == bytes([
        0xA5,
        0x82,
        0x03,
        0x01,
        0x02,
        0x03,
        expected_checksum
    ])
    assert packet[-1] == 0x24 # expected checksum value

def test_build_request_empty_payload():
    packet = build_request(RPLidarCommand.GET_INFO, b"")

    assert packet == b"\xA5\x50"

# Parsing Response Descriptor Tests
def test_parse_response_descriptor_scan():
    packet = b"\xA5\x5A\x05\x00\x00\x40\x81"

    descriptor = parse_response_descriptor(packet)

    assert descriptor.data_length == 5
    assert descriptor.send_mode == 1
    assert descriptor.data_type == 0x81

def test_parse_response_descriptor_express_scan_dense():
    packet = b"\xA5\x5A\x54\x00\x00\x40\x85"

    descriptor = parse_response_descriptor(packet)

    assert descriptor.data_length == 84
    assert descriptor.send_mode == 1
    assert descriptor.data_type == 0x85

def test_parse_response_descriptor_get_info():
    packet = b"\xA5\x5A\x14\x00\x00\x00\x04"

    descriptor = parse_response_descriptor(packet)

    assert descriptor.data_length == 20
    assert descriptor.send_mode == 0
    assert descriptor.data_type == 0x04


def test_parse_response_descriptor_get_health():
    packet = b"\xA5\x5A\x03\x00\x00\x00\x06"

    descriptor = parse_response_descriptor(packet)

    assert descriptor.data_length == 3
    assert descriptor.send_mode == 0
    assert descriptor.data_type == 0x06

def test_parse_response_descriptor_get_samplerate():
    packet = b"\xA5\x5A\x04\x00\x00\x00\x15"

    descriptor = parse_response_descriptor(packet)

    assert descriptor.data_length == 4
    assert descriptor.send_mode == 0
    assert descriptor.data_type == 0x15

def test_parse_response_descriptor_invalid_length():
    packet = b"\xA5\x5A"

    with pytest.raises(ValueError):
        parse_response_descriptor(packet)

def test_parse_response_descript_rejects_extra_bytes():
    packet = b"\xA5\x5A\x05\x00\x00\x40\x81\x00"

    with pytest.raises(ValueError):
        parse_response_descriptor(packet)

def test_parse_response_descriptor_invalid_flags():
    packet = b"\x5A\xA5\x05\x00\x00\x40\x81"

    with pytest.raises(ValueError):
        parse_response_descriptor(packet)

def test_parse_response_descript_invalid_send_mode():
    # Upper two bits are 10 from the 5-byte(0x80)
    packet = b"\xA5\x5A\x05\x00\x00\x80\x81"

    with pytest.raises(ValueError):
        parse_response_descriptor(packet)


# Parsing SCAN Mode Response Data Tests
def test_parse_scan_data_valid_first_scan_point_packet():
    packet = b"\xA5\x95\x12\xC8\x03"

    scan_data = parse_scan_data(packet)

    assert scan_data.start_flag is True
    assert scan_data.quality == 41
    assert scan_data.angle_degrees == pytest.approx(37.15624)
    assert scan_data.distance_mm == pytest.approx(242.0)

def test_parse_scan_data_valid_not_first_scan_point_packet():
    packet = b"\xA6\x2B\x15\xB1\xA2"

    scan_data = parse_scan_data(packet)

    assert scan_data.start_flag is False
    assert scan_data.quality == 41
    assert scan_data.angle_degrees == pytest.approx(42.32812)
    assert scan_data.distance_mm == pytest.approx(10412.25)

def test_parse_scan_data_zero_quality_and_distance():
    packet = b"\x01\x01\x00\x00\x00"

    scan_data = parse_scan_data(packet)

    assert scan_data.start_flag is True
    assert scan_data.quality == 0
    assert scan_data.angle_degrees == pytest.approx(0.0)
    assert scan_data.distance_mm == pytest.approx(0.0)

def test_parse_scan_data_large_angle_and_distance():
    packet = b"\x01\x01\xB2\xFF\xFF"

    scan_data = parse_scan_data(packet)

    assert scan_data.start_flag is True
    assert scan_data.quality == 0
    assert scan_data.angle_degrees == pytest.approx(356.0)
    assert scan_data.distance_mm == pytest.approx(16383.75)

def test_parse_scan_data_invalid_length():
    packet = b"\xA5\x90"

    with pytest.raises(ValueError):
        parse_scan_data(packet)

def test_parse_scan_data_invalid_flags():
    packet = b"\xA4\x95\x12\xC8\x03"

    with pytest.raises(ValueError):
        parse_scan_data(packet)

def test_parse_scan_data_invalid_check_bit():
    packet = b"\xA5\x94\x12\xC8\x03"

    with pytest.raises(ValueError):
        parse_scan_data(packet)

# Parsing GET_INFO mode response data tests
def test_parse_get_info_response():
    packet = bytes([
        0x01,
        0x05,
        0x02,
        0x10,
        *range(16)
    ])

    info = parse_get_info_response(packet)

    assert info.model == 1
    assert info.firmware_version_minor == 5
    assert info.firmware_version_major == 2
    assert info.hardware_version == 16
    assert info.serial_number == bytes(range(16))

def test_parse_get_info_preserves_binary_serial_number():
    serial_number = bytes([
        0xFF, 0x80, 0x7A, 0x00,
        0x4B, 0x34, 0x28, 0xA2, 
        0x8A, 0x2F, 0x8E, 0x9F,
        0x3A, 0x00, 0x24, 0x67
    ])

    packet = bytes([0x01, 0x05, 0x02, 0x10]) + serial_number

    info = parse_get_info_response(packet)

    assert info.serial_number == serial_number

def test_parse_get_info_response_invalid_length():
    packet = b"\xA0\x90"

    with pytest.raises(ValueError):
        parse_get_info_response(packet)


# Parsing GET_HEALTH mode response data tests
def test_parse_get_health_response():
    packet = b"\x02\x01\x00"

    health = parse_get_health_response(packet)

    assert health.status == 2
    assert health.error_code == 1

def test_parse_get_health_response_invalid_length():
    packet = b"\x02\x01"

    with pytest.raises(ValueError):
        parse_get_health_response(packet)

def test_parse_get_health_response_invalid_status():
    packet = b"\x03\x00\x00"

    with pytest.raises(ValueError):
        parse_get_health_response(packet)

@pytest.mark.parametrize("status", [0, 1, 2])
def test_parse_get_health_valid_statuses(status):
    packet = bytes([status, 0x34, 0x12])

    health = parse_get_health_response(packet)

    assert health.status == status
    assert health.error_code == 0x1234

# Parsing GET_SAMPLERATE mode response datad tests
def test_parse_get_samplerate_response():
    packet = b"\x01\x02\x34\x12"

    info = parse_get_samplerate_response(packet)

    assert info.t_standard == 0x0201
    assert info.t_express == 0x1234

def test_parse_get_samplerate_response_invalid_length():
    packet = b"\x01\x02\x00"

    with pytest.raises(ValueError):
        parse_get_samplerate_response(packet)
