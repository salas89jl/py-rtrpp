import time
import warnings
from collections.abc import Iterator


from . import protocol as prot
from .exceptions import (
    RPLidarConnectionError,
    RPLidarDeviceError,
    RPLidarProtocolError,
    RPLidarTimeoutError,
    RPLidarDriverError,
    RPLidarStateError,
    TransportConnectionError,
    TransportTimeoutError,
)
from .transport import RPLidarTransport
from .rplidar_warnings import (
    RPLidarHealthWarning,
)


class RPLidarDriver:
    def __init__(self, transport: RPLidarTransport):
        """
        Initializes the RPLidarDriver class

        :param transport: RPLidarTransport classfor low-level comms with RPLIDAR device.
        """

        self._transport = transport

        # Initialize the state of the RPLIDAR device.
        self._working_state = prot.RPLidarWorkingState.NOT_CONNECTED
        self._scanning_state = prot.RPLidarScanningState(
            is_active=False,
            packet_size=0,
            mode=prot.RPLidarScanningMode.INACTIVE,
        )

        # Initialize the health of the RPLIDAR device.
        self._health = prot.RPLidarGetHealthData(
            status=0,
            error_code=0,
        )

        self._pending_measurement: prot.RPLidarScanData | None = None

    def get_info(self) -> prot.RPLidarGetInfoData:
        """Sends GET_INFO command to the RPLIDAR device and returns parsed response object."""

        try:
            # Validate working state before sending the GET_INFO request.
            self._require_state(prot.RPLidarWorkingState.IDLE)

            # Send the GET_INFO request to the RPLIDAR device.
            self._send_request(prot.RPLidarCommand.GET_INFO)

            # Read and validate the descriptor for the GET_INFO response.
            descriptor = self._read_descriptor("GET_INFO")
            self._validate_descriptor(
                descriptor,
                command=prot.RPLidarCommand.GET_INFO,
                expected_data_length=prot.RPLidarDataLength.GET_INFO,
                expected_send_mode=prot.RPLidarSendMode.SINGLE_RESPONSE,
                expected_data_type=prot.RPLidarResponseType.DEVICE_INFO,
            )
            # Read the exact data for the GET_INFO response.
            raw_data = self._read_exactly(descriptor.data_length, "GET_INFO")

            # Parse the GET_INFO response.
            return prot.parse_get_info_response(raw_data)

        except ValueError as exc:
            raise RPLidarProtocolError(
                f"GET_INFO returned an invalid protocol response. {exc}"
            ) from exc

        except TransportTimeoutError as exc:
            raise RPLidarTimeoutError(
                f"Timed out while waiting for the GET_INFO response. {exc}"
            ) from exc
        except TransportConnectionError as exc:
            raise RPLidarConnectionError(f"Communication failed during GET_INFO. {exc}") from exc

    def get_health(self) -> prot.RPLidarGetHealthData:
        """Sends GET_HEALTH command to the RPLIDAR device and returns parsed response object"""

        # Validate working state before sending the GET_HEALTH request.
        self._require_state_in(
            prot.RPLidarWorkingState.IDLE,
            prot.RPLidarWorkingState.PROTECTION_STOP,
        )

        try:
            # Send the GET_HEALTH request to the RPLIDAR device.
            self._send_request(prot.RPLidarCommand.GET_HEALTH)

            # Read and validate the descriptor for the GET_HEALTH response.
            descriptor = self._read_descriptor("GET_HEALTH")
            self._validate_descriptor(
                descriptor,
                command=prot.RPLidarCommand.GET_HEALTH,
                expected_data_length=prot.RPLidarDataLength.GET_HEALTH,
                expected_send_mode=prot.RPLidarSendMode.SINGLE_RESPONSE,
                expected_data_type=prot.RPLidarResponseType.DEVICE_HEALTH,
            )

            # Read the exact data for the GET_HEALTH response.
            raw_data = self._read_exactly(descriptor.data_length, "GET_HEALTH")

            self._health = prot.parse_get_health_response(raw_data)

        except ValueError as exc:
            raise RPLidarProtocolError(
                f"GET_HEALTH returned an invalid protocol response. {exc}"
            ) from exc

        except TransportTimeoutError as exc:
            raise RPLidarTimeoutError(
                f"Timed out while waiting for the GET_HEALTH response. {exc}"
            ) from exc

        except TransportConnectionError as exc:
            raise RPLidarConnectionError(f"Communication failed during GET_HEALTH. {exc}") from exc

        return self._health

    def get_samplerate(self) -> prot.RPLidarGetSamplerateData:
        """Sends GET_SAMPLERATE command to the RPLIDAR device and returns parsed response object."""

        try:
            # Validate working state before sending the GET_SAMPLERATE request.
            self._require_state(prot.RPLidarWorkingState.IDLE)

            # Send the GET_SAMPLERATE request to the RPLIDAR device.
            self._send_request(prot.RPLidarCommand.GET_SAMPLERATE)

            # Read and validate the descriptor for the GET_SAMPLERATE response.
            descriptor = self._read_descriptor("GET_SAMPLERATE")

            self._validate_descriptor(
                descriptor,
                command=prot.RPLidarCommand.GET_SAMPLERATE,
                expected_data_length=prot.RPLidarDataLength.GET_SAMPLERATE,
                expected_send_mode=prot.RPLidarSendMode.SINGLE_RESPONSE,
                expected_data_type=prot.RPLidarResponseType.DEVICE_SAMPLERATE,
            )

            # Read the exact data for the GET_SAMPLERATE response.
            raw_data = self._read_exactly(descriptor.data_length, "GET_SAMPLERATE")

            # Parse the GET_SAMPLERATE response.
            return prot.parse_get_samplerate_response(raw_data)
        except ValueError as exc:
            raise RPLidarProtocolError(
                f"GET_SAMPLERATE returned an invalid protocol response. {exc}"
            ) from exc

        except TransportTimeoutError as exc:
            raise RPLidarTimeoutError(
                f"Timed out while waiting for the GET_SAMPLERATE response. {exc}"
            ) from exc

        except TransportConnectionError as exc:
            raise RPLidarConnectionError(
                f"Communication failed during GET_SAMPLERATE response. {exc} "
            ) from exc

    def stop(self) -> None:
        """Sends the STOP command to the RPLIDAR device."""
        # Validate working state before sending the STOP request.
        self._require_state(prot.RPLidarWorkingState.SCANNING)

        try:
            self._request_stop()

        except TransportConnectionError as exc:
            self._recover_from_connection_error()
            raise RPLidarConnectionError(
                f"Communication failed while stopping the RPLIDAR scan: {exc}"
            ) from exc

        except TransportTimeoutError as exc:
            self._recover_from_query_transaction_error()
            raise RPLidarTimeoutError(
                f"Communication timed out while stopping RPLIDAR scan: {exc}"
            ) from exc

        except ValueError as exc:
            raise RPLidarProtocolError(
                f"Failed to stop RPLIDAR Scanning, invalid protocol request: {exc}"
            ) from exc

        self._clear_scanning_state()
        self._working_state = prot.RPLidarWorkingState.IDLE

    def reset(self) -> None:
        """Sends the RESET command to the RPLIDAR device."""

        # Validate working state before sending the RESET request.
        self._require_state(prot.RPLidarWorkingState.PROTECTION_STOP)

        try:
            # Send the RESET request to the RPLIDAR device.
            self._send_request(prot.RPLidarCommand.RESET)
            time.sleep(prot.POST_COMMAND_DELAYS[prot.RPLidarCommand.RESET])
        except ValueError as exc:
            self._recover_from_query_transaction_error()
            raise RPLidarProtocolError(
                f"RESET returned an invalid protocol response. {exc}"
            ) from exc
        except TransportTimeoutError as exc:
            self._recover_from_query_transaction_error()
            raise RPLidarTimeoutError(
                f"Timed out while waiting for the RESET response. {exc}"
            ) from exc
        except TransportConnectionError as exc:
            self._recover_from_connection_error()
            raise RPLidarConnectionError(f"Communication failed during RESET. {exc}") from exc

        self._health = self.get_health()

        if self._health.status is not prot.RPLidarHealthStatus.ERROR:
            # Transition to IDLE state invariant if the device is not in an error state.
            self._working_state = prot.RPLidarWorkingState.IDLE
            self._clear_scanning_state()

        # Clear the transport layer's internal buffer to ensure no residual data remains.
        self._synchronize_transport_buffers()

    def connect(self) -> None:
        """Establishes a connection to the RPLIDAR device."""

        # Check for valid working state before attempting to open the connection
        self._require_state(prot.RPLidarWorkingState.NOT_CONNECTED)

        try:
            self._transport.open()
            self._set_idle_state()
            self._check_health()

        except RPLidarDeviceError:
            self._set_protection_stop_state()
            raise

        except TransportConnectionError as exc:
            self._recover_from_connection_error()
            raise RPLidarConnectionError(
                f"Failed communication opening serial connection: {exc}"
            ) from exc

        except (
            RPLidarTimeoutError,
            RPLidarProtocolError,
            RPLidarConnectionError,
        ):
            self._recover_from_connection_error()
            raise

    def disconnect(self) -> None:
        """Closes the connection to the RPLIDAR device."""

        stop_error: RPLidarConnectionError | RPLidarTimeoutError | None = None
        close_error: RPLidarConnectionError | None = None

        if self._working_state is prot.RPLidarWorkingState.SCANNING:
            stop_error = self._best_effort_stop()

        try:
            self._transport.close()

        except TransportConnectionError as exc:
            close_error = RPLidarConnectionError(f"Tranport failed to close: {exc}")

        finally:
            self._clear_scanning_state()
            self._working_state = prot.RPLidarWorkingState.NOT_CONNECTED

        if close_error is not None:
            raise close_error

        if stop_error is not None:
            raise stop_error

    def start_scan(self) -> None:
        """Enter standard SCAN mode and validate its descriptor."""
        try:
            self._require_state(prot.RPLidarWorkingState.IDLE)

            self._send_request(prot.RPLidarCommand.SCAN)
            descriptor = self._read_descriptor("SCAN")

            self._validate_descriptor(
                descriptor=descriptor,
                command=prot.RPLidarCommand.SCAN,
                expected_data_length=prot.RPLidarDataLength.SCAN_DATA,
                expected_send_mode=prot.RPLidarSendMode.MULTIPLE_RESPONSE,
                expected_data_type=prot.RPLidarResponseType.MEASUREMENT_DATA,
            )

            self._working_state = prot.RPLidarWorkingState.SCANNING

            self._clear_scanning_state()

            self._update_scanning_state(
                packet_size=descriptor.data_length,
                mode=prot.RPLidarScanningMode.STANDARD,
                response_type=prot.RPLidarResponseType.MEASUREMENT_DATA,
                completed_scan_count=0,
            )

        except TransportTimeoutError as exc:
            raise RPLidarTimeoutError(
                f"Timed out while waiting for the SCAN response descriptor. {exc}"
            ) from exc

        except TransportConnectionError as exc:
            raise RPLidarConnectionError(
                f"Communication failed attempted to enter SCAN mode. {exc}"
            ) from exc

        except ValueError as exc:
            self.stop()

            raise RPLidarProtocolError(
                f"SCAN returned an invalid protocol response descriptor. {exc}"
            ) from exc

    def iter_measurements(self) -> Iterator[prot.RPLidarScanData]:
        """Yield parsed measurements continuously until scanning stops."""

        if not self._scanning_state.is_active:
            raise RPLidarStateError("Cannot iterate measurements when scanning is not active.")
        while self._scanning_state.is_active:
            yield self._read_measurement()

    def read_scan(self) -> list[prot.RPLidarScanData]:
        """Return one complete revolution, delimited by start flag."""
        try:
            # Validate working state before attempting to read a scan.
            self._require_state(prot.RPLidarWorkingState.SCANNING)

            # Initialize the list to store one complete revolution of scan data.
            scan: list[prot.RPLidarScanData] = []

            # Check if pending measurement from the previous scan exists.
            if self._pending_measurement is not None:
                first = self._pending_measurement
                self._pending_measurement = None
            else:
                first = self._wait_for_new_scan()

            scan.append(first)

            for measurement in self.iter_measurements():
                if measurement.start_flag and scan:
                    self._pending_measurement = measurement
                    break
                scan.append(measurement)
            self._scanning_state.completed_scan_count += 1

            return scan

        except ValueError as exc:
            raise RPLidarProtocolError(
                f"Invalid protocol response while reading a complete scan. {exc}"
            ) from exc

        except TransportTimeoutError as exc:
            raise RPLidarTimeoutError(f"Timed out while reading a complete scan. {exc}") from exc

        except TransportConnectionError as exc:
            raise RPLidarConnectionError(
                f"Communication failed while reading a scan. {exc}"
            ) from exc

    def _send_request(self, command: prot.RPLidarCommand) -> None:
        """Sends a request command to the RPLIDAR device over the transport layer."""

        request = prot.build_request(command)
        self._transport.write(request)

    def _validate_descriptor(
        self,
        descriptor: prot.RPLidarResponseDescriptor,
        *,
        command: prot.RPLidarCommand,
        expected_data_length: prot.RPLidarDataLength,
        expected_send_mode: prot.RPLidarSendMode,
        expected_data_type: prot.RPLidarResponseType,
    ) -> None:
        """Validates response descriptor against expected values. Raises ValueError if fails."""

        operation = command.name

        if descriptor.data_length != expected_data_length.value:
            raise ValueError(
                f"{operation} expected {expected_data_length.value} response bytes, "
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
        try:
            data = self._transport.read(size)

        except TransportTimeoutError as exc:
            raise RPLidarTimeoutError(
                f"Time out while reading {operation} response packet. {exc}"
            ) from exc
        except TransportConnectionError as exc:
            raise RPLidarConnectionError(
                f"Connection failed while reading {operation} response packet {exc}"
            ) from exc

        return data

    def _read_descriptor(self, operation: str) -> prot.RPLidarResponseDescriptor:
        """Read and parse one seven-byte response descriptor."""

        raw_descriptor = self._read_exactly(7, operation + " descriptor")

        return prot.parse_response_descriptor(raw_descriptor)

    def _read_measurement(self) -> prot.RPLidarScanData:
        """Read and parse one measurement data response."""

        try:
            raw_data = self._read_exactly(
                self._scanning_state.packet_size,
                "SCAN measurement",
            )

            return prot.parse_scan_data(raw_data)

        except ValueError as exc:
            raise RPLidarProtocolError(
                f"Invalid protocol response while in {self._scanning_state.mode}. {exc}"
            ) from exc

    def _wait_for_new_scan(self):
        """Wait for start of new scan and return the first measurement of the new scan."""
        for measurement in self.iter_measurements():
            if measurement.start_flag:
                return measurement

        # If no start_flag is found while waiting, raise an exception
        raise RuntimeError("Unable to assemble a complete scan.")

    def _require_state(self, expected: prot.RPLidarWorkingState) -> None:
        """Ensures the RPLIDAR is in the expected working state."""
        if self._working_state != expected:
            raise RPLidarStateError(
                f"Operation requires working state {expected.name}; "
                f"current working state is {self._working_state.name}."
            )

    def _require_state_in(self, *allowed: prot.RPLidarWorkingState) -> None:
        """Ensures the RPLIDAR is in one of the allowed working states."""
        if self._working_state not in allowed:
            allowed_names = ", ".join(state.name for state in allowed)
            raise RPLidarStateError(
                f"Operation requires working state in [{allowed_names}]; "
                f"current working state is {self._working_state.name}."
            )

    def _clear_scanning_state(self) -> None:
        """Returns the scanning state to INACTIVE."""
        self._scanning_state.is_active = False
        self._scanning_state.packet_size = 0
        self._scanning_state.mode = prot.RPLidarScanningMode.INACTIVE
        self._scanning_state.completed_scan_count = 0
        self._scanning_state.response_type = None

        self._pending_measurement = None

    def _update_scanning_state(
        self,
        packet_size: int,
        mode: prot.RPLidarScanningMode,
        response_type: prot.RPLidarResponseType,
        completed_scan_count: int,
    ) -> None:
        """Updates the current scanning state with new values."""
        self._scanning_state.is_active = True
        self._scanning_state.packet_size = packet_size
        self._scanning_state.mode = mode
        self._scanning_state.completed_scan_count = completed_scan_count
        self._scanning_state.response_type = response_type

    def _check_health(self) -> None:
        """Checks health status of the RPLIDAR device and report warnings or errors if any."""

        try:
            self._send_request(prot.RPLidarCommand.GET_HEALTH)

            # Read and validate the descriptor for GET_HEALTH response.
            descriptor = self._read_descriptor("GET_HEALTH")
            self._validate_descriptor(
                descriptor=descriptor,
                command=prot.RPLidarCommand.GET_HEALTH,
                expected_data_length=prot.RPLidarDataLength.GET_HEALTH,
                expected_send_mode=prot.RPLidarSendMode.SINGLE_RESPONSE,
                expected_data_type=prot.RPLidarResponseType.DEVICE_HEALTH,
            )

            raw_health_data = self._read_exactly(descriptor.data_length, "GET_HEALTH")

            self._health = prot.parse_get_health_response(raw_health_data)

        except ValueError as exc:
            self._recover_from_query_transaction_error()
            raise RPLidarProtocolError(f"Invalid protocol response. {exc}") from exc

        except TransportTimeoutError as exc:
            self._recover_from_query_transaction_error()
            raise RPLidarTimeoutError(
                f"Time out while waiting for GET_HEALTH response descriptor. {exc}"
            ) from exc

        except TransportConnectionError as exc:
            self._recover_from_connection_error()
            raise RPLidarConnectionError(
                f"Communication failure checking health while connecting. {exc}"
            ) from exc

        if self._health.status == prot.RPLidarHealthStatus.ERROR.value:
            self._working_state = prot.RPLidarWorkingState.PROTECTION_STOP
            self._clear_scanning_state()

            raise RPLidarDeviceError(
                f"RPLIDAR reported an internal error: 0x{self._health.error_code:04X}"
            )

        if self._health.status == prot.RPLidarHealthStatus.WARNING.value:
            warnings.warn(
                "The RPLIDAR reported a potential risk that may cause "
                f"future hardware failure. Error code: 0x{self._health.error_code:04X}",
                RPLidarHealthWarning,
                stacklevel=2,
            )

    def _recover_from_stream_error(self) -> None:
        """
        Recover from timeout or protocol error during a scan stream.
        Resets the transport buffers and clears the scanning state.
        """

        try:
            self._send_request(prot.RPLidarCommand.STOP)
            time.sleep(prot.POST_COMMAND_DELAYS[prot.RPLidarCommand.STOP])

            self._synchronize_transport_buffers()

        except ValueError as exc:
            raise RPLidarProtocolError(f"Invalid protocol request. {exc}") from exc

        except TransportConnectionError as exc:
            self._recover_from_connection_error()
            raise RPLidarConnectionError(
                f"Communication failed during stream recovery. {exc}"
            ) from exc

        self._clear_scanning_state()
        self._working_state = prot.RPLidarWorkingState.IDLE

    def _recover_from_connection_error(self) -> None:
        """Recover from a fatal transport connection failure.

        Performs best-effort transport cleanup, clears all scan-related state,
        and transitions the driver to NOT_CONNECTED.
        """

        try:
            self._transport.close()
        except TransportConnectionError:
            pass

        finally:
            self._transport.clear_internal_buffer()
            self._set_not_connected_state()

    def _recover_from_query_transaction_error(self):
        """Recovers from timout or protocol error during query transactions."""

        try:
            self._synchronize_transport_buffers()
        except TransportConnectionError as exc:
            self._recover_from_connection_error()
            raise RPLidarConnectionError(f"Failed to synchronize transport buffers. {exc}") from exc

    def _synchronize_transport_buffers(self) -> None:
        """Synchronizes the transport buffers to ensure a clean state."""
        self._transport.flush()
        self._transport.reset_io_buffers()
        self._transport.clear_internal_buffer()

    def _set_idle_state(self) -> None:
        """Sets driver to IDLE invariant state."""
        self._working_state = prot.RPLidarWorkingState.IDLE
        self._clear_scanning_state()

    def _set_protection_stop_state(self) -> None:
        """Sets driver to PROTECTION_STOP invariant state."""
        self._working_state = prot.RPLidarWorkingState.PROTECTION_STOP
        self._clear_scanning_state()

    def _set_not_connected_state(self) -> None:
        """Sets driver to NOT_CONNECTED invariant state."""
        self._working_state = prot.RPLidarWorkingState.NOT_CONNECTED
        self._clear_scanning_state()

    def _request_stop(self) -> None:
        # Send the STOP request to the RPLIDAR device.
        self._send_request(prot.RPLidarCommand.STOP)
        time.sleep(prot.POST_COMMAND_DELAYS[prot.RPLidarCommand.STOP])

        # Clear the transport layer's internal buffer to ensure no residual data remains.
        self._synchronize_transport_buffers()

    def _best_effort_stop(self) -> RPLidarConnectionError | RPLidarTimeoutError | None:
        """
        Attempt to stop the RPLIDAR without interrupting cleanup.

        Returns:
            The translated STOP exception if stopping fails.
            Otherwise, returns None.
        """

        try:
            self._request_stop()

        except TransportConnectionError as exc:
            return RPLidarConnectionError(f"Communication failed during STOP: {exc}")
        except TransportTimeoutError as exc:
            return RPLidarTimeoutError(f"Communication timed out during STOP: {exc}")

        finally:
            self._clear_scanning_state()

        return None

    @property
    def scanning_state(self) -> prot.RPLidarScanningState:
        # Returns the current scanning state of the RPLIDAR device.
        STATE = self._scanning_state
        return STATE

    @property
    def working_state(self) -> prot.RPLidarWorkingState:
        # Returns the current working state of the RPLIDAR device.
        STATE = self._working_state
        return STATE
