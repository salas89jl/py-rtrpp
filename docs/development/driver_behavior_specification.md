# Driver Behavior Specification

An invariant is a condition, relationship, or property that remains true throughout the execution of a program or during the lifetime of an object. In the context of the RPLIDAR Driver, state invariants ensure that the driver operates correctly by maintaining consistent and valid states.

This is why implementing proper state management is crucial for ensuring the correctness and reliability of the RPLIDAR Driver. To ensure that the driver enforces proper state transitions, it must validate the current state before executing any operation and only allow transitions that adhere to the defined state invariants.

In order to enforce these state invariants, the driver layer implements state guards and recovery mechanisms. These state guards check the current state of the driver before allowing any operation to proceed, ensuring that the driver only performs actions that are valid for its current state. This prevents illegal state transitions and maintains the integrity of the driver's state.

The driver layer uses the following state guards to enforce the driver state invariants:
- `_require_state(state: RPLidarWorkingState) -> None`: Ensures the driver is in the specified working state.
- `_require_state_in(*states: RPLidarWorkingState) -> None`: Ensures the driver is in one of the allowed working states.

Additionally, the driver layer implements the following internal methods to manage the scanning state and ensure that it remains consistent with the driver's working state:
- `_clear_scanning_state() -> None`: Clears the current scanning state and sets default values for the scanning state attributes.
- `_update_scanning_state(packet_size: int, mode: RPLidarScanningMode, response_type: RPLidarResponseType, completed_scan_count: int) -> None`: Updates the current scanning state with new values.
- `_check_health() -> None`: Checks the health status of the RPLIDAR device and transitions the driver into the `PROTECTION_STOP` state if a health error is detected.


In addition to the state guards, the driver layer implements recovery mechanisms to handle errors and maintain a consistent state. These recovery mechanisms are designed to ensure that the driver can recover from various error conditions without leaving the driver in an inconsistent or invalid state. The recovery mechanisms include:

- `_recover_from_stream_error() -> None`: Attempts to recover from a stream error by stopping the scan and clearing the scanning state.
- `_recover_from_connection_error() -> None`: Recovers from a fatal transport connection failure.
- `_synchronize_transport_buffers() -> None`: Synchronizes the transport's software buffers by completing output transmission, resetting the input and output buffers, and clearing the transport's internal software buffer.

## Defined Internal Driver States

__IDLE Driver State:__
- [ ] `working_state == IDLE`
- [ ] `scanning_state.is_active is False`
- [ ] `scanning_state.mode == INACTIVE`
- [ ] `scanning_state.response_type is None`
- [ ] `scanning_state.packet_size == 0`
- [ ] `scanning_state.completed_scan_count == 0`
- [ ] `_pending_measurement is None`

__SCANNING Driver State:__
- [ ] `working_state == SCANNING`
- [ ] `scanning_state.is_active is True`
- [ ] `scanning_state.mode == STANDARD_SCAN`
- [ ] `scanning_state.response_type == MEASUREMENT_DATA`
- [ ] `scanning_state.packet_size == 5`
- [ ] `scanning_state.completed_scan_count >= 0`
- [ ] Counts only complete scans returned since the most recent successful
      `start_scan()`
- [ ] `_pending_measurement is None` or
      `isinstance(_pending_measurement, RPLidarScanData)`
- [ ] If `_pending_measurement` is not `None`,
      `_pending_measurement.start_flag is True`

__NOT_CONNECTED Driver State:__
- [ ] `working_state == NOT_CONNECTED`
- [ ] `scanning_state.is_active is False`
- [ ] `scanning_state.mode == INACTIVE`
- [ ] `scanning_state.response_type is None`
- [ ] `scanning_state.packet_size == 0`
- [ ] `scanning_state.completed_scan_count == 0`
- [ ] `_pending_measurement is None`

__PROTECTION_STOP Driver State:__
- [ ] `working_state == PROTECTION_STOP`
- [ ] `scanning_state.is_active is False`
- [ ] `scanning_state.mode == INACTIVE`
- [ ] `scanning_state.response_type is None`
- [ ] `scanning_state.packet_size == 0`
- [ ] `scanning_state.completed_scan_count == 0`
- [ ] `_pending_measurement is None`

## Invariants Checklist for Every Driver Operation

### __connect()__:
Valid starting states:
- [ ] Driver satisfies `NOT_CONNECTED` state invariants
  

Successful resulting state:
- Health status is `GOOD`:
  - [ ] Transport is open
  - [ ] Driver transitions to `IDLE`
  - [ ] Driver satisfies `IDLE` state invariants

- Health status is `WARNING`:
  - [ ] A health warning is emitted
  - [ ] Transport is open
  - [ ] Driver transitions to `IDLE`
  - [ ] Driver satisfies `IDLE` state invariants

Raises:
- `RPLidarStateError`
- `RPLidarConnectionError`
- `RPLidarTimeoutError`
- `RPLidarProtocolError`
- `RPLidarDeviceError`

Internal handling:
- Catches `TransportConnectionError`
- Catches `TransportTimeoutError`
- Catches `ValueError`
- Validates and parses the health response
- Maps the reported device health status to either `IDLE` or
  `PROTECTION_STOP`

Recovery:
- `RPLidarStateError`
  - [ ] No connection attempt is made
  - [ ] Transport state remains unchanged
  - [ ] Driver state remains unchanged

- `RPLidarTimeoutError`
  - [ ] Transport clousure is attempted
  - [ ] Transport internal buffer is cleared
  - [ ] Driver satisfies `NOT_CONNECTED` state invariants

- `RPLidarProtocolError`
  - [ ] Transport clousure is attempted
  - [ ] Transport internal buffer is cleared
  - [ ] Driver satisfies `NOT_CONNECTED` state invariants

- `RPLidarConnectionError`
  - [ ] Connection-error recovery is performed
  - [ ] Driver satisfies `NOT_CONNECTED` state invariants 

- `RPLidarDeviceError`
  - [ ] Device health status is `ERROR`
  - [ ] Transport remains open
  - [ ] Driver transitions to `PROTECTION_STOP`
  - [ ] Driver satisfies `PROTECTION_STOP` state invariants
  - [ ] RESET is not attempted automatically

### __disconnect()__:
Valid starting states:
- [ ] Driver may satisfy `NOT_CONNECTED`, `IDLE`, `SCANNING`, or `PROTECTION_STOP` state invariants

Successful resulting state:
- [ ] Transport close is attempted
- [ ] Scan state is cleared
- [ ] `_pending_measurement is None`
- [ ] Driver transitions to `NOT_CONNECTED`
- [ ] Driver satisfies `NOT_CONNECTED` state invariants

State-specific handling:

- Starting state is `SCANNING`:
- [ ] STOP is requested as a best-effort operation
- [ ] A STOP failure does not prevent transport closure
- [ ] Scan state is cleared
- [ ] Transport close is attempted
- [ ] Driver satisfies `NOT_CONNECTED` state invariants

- Starting state is `IDLE`:
- [ ] No STOP command is required
- [ ] Transport close is attempted
- [ ] Driver satisfies `NOT_CONNECTED` state invariants

- Starting state is `PROTECTION_STOP`:
- [ ] No STOP command is required
- [ ] Transport close is attempted
- [ ] Driver satisfies `NOT_CONNECTED` state invariants

- Starting state is `NOT_CONNECTED`:
- [ ] No STOP command is required
- [ ] Driver remains in `NOT_CONNECTED` state
- [ ] Driver satisfies `NOT_CONNECTED` state invariants

Raises:
- `RPLidarConnectionError`
  - When communication fails during STOP or when the transport closure fails
- `RPLidarStateError`
  - If the driver reports `SCANNING` but does not satisfy the complete
    `SCANNING` state invariants required by `stop()`

Exception precedence:
- [ ] If only STOP fails, the STOP exception is propagated after cleanup
- [ ] If transport closure fails, `RPLidarConnectionError` from closure is raised
- [ ] If both fail, the transport-closure error takes precedence

Internal handling:
- Calls `stop()` when the starting state is `SCANNING`
- Attempts transport closure regardless of STOP outcome
- Clears scan state and `_pending_measurement` in final cleanup
- Transitions the driver to `NOT_CONNECTED`
- Raises the applicable driver exception after cleanup, if required

Recovery from `stop()` method:

- STOP operation fails:
- [ ] Transport closure is still attempted
- [ ] Scan state is cleared
- [ ] `_pending_measurement` is `None`
- [ ] Driver transitions to `NOT_CONNECTED`
- [ ] Driver satisfies `NOT_CONNECTED` state invariants

- Transport closure fails:
- [ ] Scan state is cleared
- [ ] `_pending_measurement` is `None`
- [ ] Driver transitions to `NOT_CONNECTED`
- [ ] Driver satisfies `NOT_CONNECTED` state invariants


### __start_scan()__:
Valid starting states:
- [ ] Driver satisfies `IDLE` state invariants
  
Successful resulting state:
- [ ] `scanning_state.completed_scan_count == 0`
- [ ] Driver enters `SCANNING` state
- [ ] Driver satisfies `SCANNING` state invariants
- [ ] No stale measurement from a previous scan session remains pending

Raises:
- `RPLidarStateError`
- `RPLidarProtocolError`
- `RPLidarConnectionError`
- `RPLidarTimeoutError`

Internal handling:
- Catches ValueError
- Catches TransportTimeoutError
- Catches TransportConnectionError
- Attempts scan recovery when appropriate
- Clears scan state on failure

Recovery:
- `RPLidarStateError` 
- [ ] No command is sent
- [ ] Existing driver state remains unchanged
  
- `RPLidarProtocolError`
- [ ] Stream recovery protocol is applied when a SCAN request was sent, but the response was invalid.
- [ ] Driver satisfies `IDLE` invariants when recovery succeeds
  
- `RPLidarTimeoutError`
- [ ] Stream recovery protocol is applied when a SCAN request was sent, but the expected response was not received in time.
- [ ] Driver satisfies `IDLE` invariants when recovery succeeds

- `RPLidarConnectionError`
  - [ ] Connection-error recovery is performed
  - [ ] Driver satisfies `NOT_CONNECTED` state invariants

### __read_scan()__:

Valid starting states:
- [ ] Driver satisfies `SCANNING` state invariants
  
Successful resulting state:
- [ ] `scanning_state.completed_scan_count` is incremented by exactly 1
- [ ] Returned scan begins with `start_flag is True`
- [ ] The next revolution’s first measurement is not included in the returned scan.
- [ ] The pending boundary measurement is stored exactly once.
- [ ] `_pending_measurement.start_flag is True`
- [ ] No measurement is lost or duplicated by driver boundary handling
- [ ] Returns one complete scan revolution
- [ ] Driver continues to satisfy `SCANNING` state invariants


Raises:
- `RPLidarStateError`
- `RPLidarProtocolError`
- `RPLidarTimeoutError`
- `RPLidarConnectionError`

Internal handling:
- Catches ValueError
- Catches TransportTimeoutError
- Catches TransportConnectionError
- Attempts scan recovery when appropriate
- Clears scan state on failure

Recovery:
- `RPLidarStateError`
- [ ] No command is sent
- [ ] Existing driver state remains unchanged
  
- `RPLidarProtocolError`
- [ ] Stream recovery policy is applied when a SCAN response is invalid.
- [ ] Driver satisfies `IDLE` invariants when recovery succeeds
  
- `RPLidarTimeoutError`
- [ ] Stream recovery policy is applied when a SCAN response is not received in time.
- [ ] Driver satisfies `IDLE` invariants when recovery succeeds

- `RPLidarConnectionError`
  - [ ] Connection-error recovery is performed
  - [ ] Driver satisfies `NOT_CONNECTED` state invariants 

### __stop()__:
Valid starting states:
- [ ] Driver satisfies `SCANNING` state invariants
  
Successful resulting state:
- [ ] `scanning_state.is_active is False`
- [ ] `scanning_state.mode == INACTIVE`
- [ ] `scanning_state.response_type is None`
- [ ] `scanning_state.packet_size == 0`
- [ ] `scanning_state.completed_scan_count` is unchanged
- [ ] `_pending_measurement` is `None`
- [ ] Driver enters `IDLE` state
- [ ] Driver satisfies `IDLE` state invariants

Transport effects:
- [ ] STOP request is written to the transport
- [ ] Required post-command delay is observed
- [ ] Pending output transmission is completed
- [ ] Serial input and output buffers are reset
- [ ] Transport's internal software buffer is reset

Raises:
- `RPLidarStateError`
- `RPLidarConnectionError`
  
Internal handling:
- Catches TransportConnectionError

Recovery:
- `RPLidarStateError`
  - [ ] No command is sent
  - [ ] Transport's internal software buffer remains unchanged
  - [ ] Existing driver state remains unchanged

- `RPLidarConnectionError`
  - [ ] Connection-error recovery is performed
  - [ ] Driver satisfies `NOT_CONNECTED` state invariants if recovery succeeds.

### __reset()__:
Valid starting states:
- [ ] Driver satisfies `PROTECTION_STOP` invariants
  
Successful resulting state:
- [ ] Device returns a valid health response
- [ ] Health status is `GOOD` or `WARNING`
- [ ] A health warning is emitted when the status is `WARNING`
- [ ] Scan state is cleared
- [ ] `_pending_measurement` is `None`
- [ ] Driver transitions to `IDLE`
- [ ] Driver satisfies `IDLE` invariants

Transport effects:
- [ ] RESET request is written to the transport
- [ ] Required post-command delay is observed
- [ ] Pending output transmission is completed
- [ ] Serial input and output buffers are reset
- [ ] Transport's internal software buffer is reset
- [ ] Health request is written to the transport
- [ ] Health response is read and validated

Raises:
- `RPLidarStateError`
- `RPLidarDeviceError`
- `RPLidarConnectionError`
- `RPLidarTimeoutError`
- `RPLidarProtocolError`

Internal handling:
- Catches TransportConnectionError
- Catches TransportTimeoutError
- Parses and validates the health response
- Maps the reported health status to `IDLE` or `PROTECTION_STOP`

Recovery:
- `RPLidarStateError`
  - [ ] No command is sent
  - [ ] Existing driver state remains unchanged

- `RPLidarDeviceError`
  - [ ] Device health status is `ERROR`
  - [ ] Driver remains in `PROTECTION_STOP`
  - [ ] Driver satisfies `PROTECTION_STOP` invariants

- `RPLidarTimeoutError`
  - [ ] Query Transaction Recovery is performed
  - [ ] Driver remains in `PROTECTION_STOP` if recovery succeeds
  - [ ] Driver satisfies `PROTECTION_STOP` invariants

- `RPLidarProtocolError`
  - [ ] Query Transaction Recovery is performed
  - [ ] Driver remains in `PROTECTION_STOP` if recovery succeeds
  - [ ] Driver satisfies `PROTECTION_STOP` invariants

- `RPLidarConnectionError`
  - [ ] Connection-error recovery is performed
  - [ ] Driver satisfies `NOT_CONNECTED` state invariants 


### __get_info()__:
Valid starting states:
- [ ] Driver may satisfy `IDLE` or `PROTECTION_STOP` state invariants

Successful resulting state:
- [ ] Driver continues to satisfy its starting state invariants

Raises:
- `RPLidarStateError`
- `RPLidarProtocolError`
- `RPLidarTimeoutError`
- `RPLidarConnectionError`

Internal handling:
- Catches ValueError
- Catches TransportTimeoutError
- Catches TransportConnectionError
- Parses and validates the GET_INFO response
  
Recovery:
- `RPLidarStateError`
- [ ] No command is sent
- [ ] Existing driver state remains unchanged

- `RPLidarProtocolError`
- [ ] Query transaction recovery is performed
- [ ] Starting driver state remains unchanged if recovery succeeds.

- `RPLidarTimeoutError`
  - [ ] Query transaction recovery is performed
- [ ] Driver remains in starting state if recovery succeeds.

- `RPLidarConnectionError`
- [ ] Connection-error recovery is performed
- [ ] Driver satisfies `NOT_CONNECTED` state invariants

### __get_health()__:

Valid starting states:
- [ ] Driver may satisfy `IDLE` or `PROTECTION_STOP` state invariants

Successful resulting state:
- [ ] Device returns a valid health response

- Starting state is `IDLE`:
  - Health status is `GOOD`:
    - [ ] Driver remains in `IDLE`
    - [ ] Driver satisfies `IDLE` state invariants

  - Health status is `WARNING`:
    - [ ] A health warning is emitted
    - [ ] Driver remains in `IDLE`
    - [ ] Driver satisfies `IDLE` state invariants

- Starting state is `PROTECTION_STOP`:
  - Health status is `GOOD`:
    - [ ] Driver remains in `PROTECTION_STOP`
    - [ ] Driver satisfies `PROTECTION_STOP` state invariants
    - [ ] No automatic transition to `IDLE` occurs

  - Health status is `WARNING`:
    - [ ] A health warning is emitted
    - [ ] Driver remains in `PROTECTION_STOP`
    - [ ] Driver satisfies `PROTECTION_STOP` state invariants
    - [ ] No automatic transition to `IDLE` occurs

Device health error:
- Health status is `ERROR`:
  - [ ] Driver transitions to or remains in `PROTECTION_STOP`
  - [ ] Driver satisfies `PROTECTION_STOP` state invariants
  - [ ] `RPLidarDeviceError` is raised
  - [ ] RESET is not attempted automatically

Raises:
- `RPLidarStateError`
- `RPLidarProtocolError`
- `RPLidarTimeoutError`
- `RPLidarConnectionError`
- `RPLidarDeviceError`

Recovery:

- `RPLidarStateError`
  - [ ] No command is sent
  - [ ] Existing driver state remains unchanged

- `RPLidarProtocolError`
  - [ ] Query transaction recovery is performed
  - [ ] Starting driver state remains unchanged if recovery succeeds

- `RPLidarTimeoutError`
  - [ ] Query transaction recovery is performed
  - [ ] Starting driver state remains unchanged if recovery succeeds

- `RPLidarConnectionError`
  - [ ] Connection-error recovery is performed
  - [ ] Driver satisfies `NOT_CONNECTED` state invariants

- `RPLidarDeviceError`
  - [ ] Health status is `ERROR`
  - [ ] Driver satisfies `PROTECTION_STOP` state invariants

### __get_samplerate()__:
Valid starting states:
- [ ] Driver may satisfy `IDLE` or `PROTECTION_STOP` state invariants
Successful resulting state:
- [ ] Driver continues to satisfy its starting state invariants

Raises:
- `RPLidarStateError`
- `RPLidarProtocolError`
- `RPLidarTimeoutError`
- `RPLidarConnectionError`

Internal handling:
- Catches ValueError
- Catches TransportTimeoutError
- Catches TransportConnectionError
- Parses and validates the GET_SAMPLERATE response
  
Recovery:
- `RPLidarStateError`
- [ ] No command is sent
- [ ] Existing driver state remains unchanged

- `RPLidarProtocolError`
- [ ] Query transaction recovery is performed
- [ ] Driver continues to satisfy its starting state invariants

- `RPLidarTimeoutError`
- [ ] Query transaction recovery is performed
- [ ] Driver continues to satisfy its starting state invariants

- `RPLidarConnectionError`
- [ ] Connection-error recovery is performed
- [ ] Driver satisfies `NOT_CONNECTED` state invariants

## __Recovery Policy__:

### __Stream Recovery:__

Stream recovery defines the guaranteed driver state after a timeout or protocol error invalidates the active measurement stream. In either case, the driver can no longer assume the packet boundaries remain synchronized with the device's output stream. 

Stream recovery applies when:
- [ ] The driver is currently in the `SCANNING` state; or
- [ ] A SCAN request was sent, but the startup failed before the transition to the `SCANNING` state was completed.

If the transport is open:
- STOP recovery is attempted
- [ ] If STOP recovery succeeds:
  - [ ] Transport buffers are synchronized
  - [ ] Driver satisfies `IDLE` state invariants

If the transport is closed, or STOP recovery encountered a connection error:
- [ ] Connection-error recovery is performed
- [ ] The driver transitions to the `NOT_CONNECTED` state

- [ ] The transport is **not** automatically reopened
- [ ] The user must call `connect()` to reestablish the connection

### __Connection Recovery:__

A connection error indicates that the transport can no longer be considered usable. The underlying cause may include physical disconnection, hardware failure, operating system I/O errors, or other transport-level failures.

Recovery actions (best effort):

- [ ] Attempt to close the transport connection
- [ ] Clear transport's internal software buffer
- [ ] Clear driver's scan state and `_pending_measurement`

Guaranteed postconditions:

- [ ] Driver satisfies `NOT_CONNECTED` state invariants
- [ ] The transport is no longer considered usable
- [ ] Automatic reconnection is not attempted
- [ ] The caller must explicitly invoke `connect()` to establish a new connection.

### __Query Transaction Recovery:__

Query transaction recovery defines the guaranteed driver state after a timeout or protocol error occurs during a query transaction. A query transaction is defined as any operation that sends a request to the device and expects a response, such as `get_info()`, `get_health()`, or `get_samplerate()`. Additionally, query transaction recovery applies to the `reset()` or `stop()` operations, which also involve sending a request and expecting a response from the device.

#### Driver state: `IDLE`

If transport synchronization succeeds:
- [ ] Driver remains in the `IDLE` state
- [ ] Driver satisfies `IDLE` state invariants

If transport synchronization fails, or a connection error occurs:
- [ ] Connection-error recovery is performed
- [ ] The driver transitions to the `NOT_CONNECTED` state
- [ ] Driver satisfies `NOT_CONNECTED` state invariants

#### Driver state: `PROTECTION_STOP`

If transport synchronization succeeds:
- [ ] Driver remains in the `PROTECTION_STOP` state
- [ ] Driver satisfies `PROTECTION_STOP` state invariants

If transport synchronization fails, or a connection error occurs:
- [ ] Connection-error recovery is performed
- [ ] The driver transitions to the `NOT_CONNECTED` state
- [ ] Driver satisfies `NOT_CONNECTED` state invariants


### __Reset Recovery:__

Starting state:

- [ ] Driver satisfies `PROTECTION_STOP` state invariants

If RESET succeeds and health reports `GOOD` or `WARNING`:

- [ ] Driver transitions to `IDLE`
- [ ] Driver satisfies `IDLE` state invariants
- [ ] A warning is emitted if health reports `WARNING`

If health still reports `ERROR`:

- [ ] Driver remains in `PROTECTION_STOP`
- [ ] Driver satisfies `PROTECTION_STOP` state invariants
- [ ] `RPLidarDeviceError` is raised


### Device Health Error Policy

A device health error occurs when the RPLIDAR reports a health status of
`ERROR`. The device is considered connected but unavailable for normal
operation.

Guaranteed postconditions:

- [ ] Scan state is cleared
- [ ] `_pending_measurement is None`
- [ ] Driver transitions to `PROTECTION_STOP`
- [ ] Driver satisfies `PROTECTION_STOP` state invariants
- [ ] `RPLidarDeviceError` is raised
- [ ] RESET is not attempted automatically
- [ ] The caller must explicitly invoke `reset()` to attempt device recovery