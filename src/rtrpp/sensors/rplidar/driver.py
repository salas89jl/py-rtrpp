from .transport import RPLidarTransport
from .exceptions import (
    RPLidarConnectionError,
    RPLidarDeviceError,
    RPLidarProtocolError,
    RPLidarTimeoutError
)
from . import protocol as prot

import serial

class RPLidarDriver:
    def __init__(self, transport: RPLidarTransport):
        """
        Initializes the RPLidarDriver class

        :param transport: RPLidarTransport class responsible for low-level communication with RPLIDAR device.
        """
        
        self._transport = transport

    def get_info(self) -> prot.RPLidarGetInfoData:
        """ Sends the GET_INFO command to the RPLIDAR device and returns the parsed response object. """
        try:

            self._send_request(prot.RPLidarCommand.GET_INFO)

            descriptor = self._read_descriptor("GET_INFO")

            self._validate_descriptor(
                descriptor,
                command=prot.RPLidarCommand.GET_INFO,
                expected_data_length=prot.RPLidarDataLength.GET_INFO,
                expected_send_mode=prot.RPLidarSendMode.SINGLE_RESPONSE,
                expected_data_type=prot.RPLidarResponseType.DEVICE_INFO
            )

            raw_data = self._transport.read(descriptor.data_length)
            return prot.parse_get_info_response(raw_data)
        
        except ValueError as exc:
            raise RPLidarProtocolError(
                "GET_INFO returned an invalid protocol response."
            ) from exc
        
        except TimeoutError as exc:
            raise RPLidarTimeoutError(
                "Timed out while waiting for the GET_INFO response."
            ) from exc
        
        except (serial.SerialException, OSError, RuntimeError) as exc:
            raise RPLidarConnectionError(
                "Communication failed during GET_INFO."
            ) from exc

    def get_health(self) -> prot.RPLidarGetHealthData:
        """ Sends the GET_HEALTH command to the RPLIDAR device and returns the parsed response object"""

        try:
            self._send_request(prot.RPLidarCommand.GET_HEALTH)

            descriptor = self._read_descriptor("GET_HEALTH")

            self._validate_descriptor(
                descriptor,
                command=prot.RPLidarCommand.GET_HEALTH,
                expected_data_length=prot.RPLidarDataLength.GET_HEALTH,
                expected_send_mode=prot.RPLidarSendMode.SINGLE_RESPONSE,
                expected_data_type=prot.RPLidarResponseType.DEVICE_HEALTH
            )

            raw_data = self._transport.read(descriptor.data_length)

            health = prot.parse_get_health_response(raw_data)

            if health.status == 2:
                raise RPLidarDeviceError(
                    f"RPLIDAR reported an internal error: 0x{health.error_code:04X}"
                )
            return health
        
        except ValueError as exc:
            raise RPLidarProtocolError(
                "GET_HEALTH returned an invalid protocol response."
            ) from exc
        
        except TimeoutError as exc:
            raise RPLidarTimeoutError(
                "Timed out while waiting for the GET_HEALTH response."
            ) from exc
        
        except (serial.SerialException, OSError, RuntimeError) as exc:
            raise RPLidarConnectionError(
                "Communication failed during GET_HEALTH."
            ) from exc

    def get_samplerate(self) -> prot.RPLidarGetSamplerateData:
        """ Sends the GET_SAMPLERATE command to the RPLIDAR device and returns the parsed response object. """

        try:

            self._send_request(prot.RPLidarCommand.GET_SAMPLERATE)

            descriptor = self._read_descriptor("GET_SAMPLERATE")
            self._validate_descriptor(
                descriptor,
                command=prot.RPLidarCommand.GET_SAMPLERATE,
                expected_data_length=prot.RPLidarDataLength.GET_SAMPLERATE,
                expected_send_mode=prot.RPLidarSendMode.SINGLE_RESPONSE,
                expected_data_type=prot.RPLidarResponseType.DEVICE_SAMPLERATE
            )

            raw_data = self._transport.read(descriptor.data_length)
            return prot.parse_get_samplerate_response(raw_data)
        
        except ValueError as exc:
            raise RPLidarProtocolError(
                "GET_SAMPLERATE returned an invalid protocol response."
            ) from exc
        
        except TimeoutError as exc:
            raise RPLidarTimeoutError(
                "Timed out while waiting for the GET_SAMPLERATE response."
            ) from exc
        
        except (serial.SerialException, OSError, RuntimeError) as exc:
            raise RPLidarConnectionError(
                "Communication failed during GET_SAMPLERATE response. "
            ) from exc
        
    def stop(self) -> None:
        """ Sends the STOP command to the RPLIDAR device. """

        try: 
            self._send_request(prot.RPLidarCommand.STOP)

        except (serial.SerialException, OSError, RuntimeError) as exc:
            raise RPLidarConnectionError(
                "Communication failed during STOP. "
            ) from exc
        
    def reset(self) -> None:
        """ Sends the RESET command to the RPLIDAR device. """

        try:
            self._send_request(prot.RPLidarCommand.RESET)

        except (serial.SerialException, OSError, RuntimeError) as exc:
            raise RPLidarConnectionError(
                "Communication failed during RESET. "
            ) from exc


    def _send_request(self, command: prot.RPLidarCommand) -> None:
        """ Sends a request command to the RPLIDAR device. """
        request = prot.build_request(command)
        self._transport.write(request)

    def _validate_descriptor(
            self,
            descriptor: prot.RPLidarResponseDescriptor,
            *,
            command: prot.RPLidarCommand,
            expected_data_length: int,
            expected_send_mode: prot.RPLidarSendMode,
            expected_data_type: prot.RPLidarResponseType
    ) -> None:
        """ Validates the response descriptor against expected values. Raises ValueError if validation fails.
        """
        operation = command.name

        if descriptor.data_length != expected_data_length:
            raise ValueError(
                f"{operation} expected {expected_data_length} response bytes, "
                f"received descriptor length {descriptor.data_length}."
            )

        if descriptor.send_mode != expected_send_mode.value:
            raise ValueError(
                f"{operation} expected send mode {expected_send_mode}, "
                f"but got {descriptor.send_mode}."
            )

        if descriptor.data_type != expected_data_type.value:
            raise ValueError(
                f"{operation} expected data type {expected_data_type}, "
                f"but got {descriptor.data_type}."
            )

    def _read_exactly(self, size: int, operation: str) -> bytes:
        """Reads exactly the specfied number of bytes from the RPLIDAR device."""
        data = self._transport.read(size)

        if len(data) != size:
            raise RPLidarTimeoutError(
                f"{operation} expected {size} bytes but received {len(data)}."
            )
        
        return data

    def _read_descriptor(self, operation: str) -> prot.RPLidarResponseDescriptor:
        """ Read and parse one seven-byte response descriptor."""
        raw_descriptor = self._read_exactly(7, operation + " descriptor")
        return prot.parse_response_descriptor(raw_descriptor)