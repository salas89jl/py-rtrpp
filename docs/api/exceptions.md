# RPLIDAR Exceptions

The following exceptions are defined for handling errors related to the RPLIDAR device:

| Exception | Description |
|-----------|-------------|
| `RPLidarError` | Base exception class for all RPLIDAR-related errors. |
| `RPLidarConnectionError` | Raised when communication with the RPLIDAR device fails. |
| `RPLidarProtocolError` | Raised when received data violates the RPLIDAR protocol. |
| `RPLidarTimeoutError` | Raised when a timeout occurs during communication with the RPLIDAR device. |
| `RPLidarDeviceError` | Raised when the RPLIDAR device reports an error status. |

## Usage Example

```python
from rtrpp.sensors.rplidar.exceptions import (
    RPLidarError,
    RPLidarConnectionError,
    RPLidarProtocolError,
    RPLidarTimeoutError,
    RPLidarDeviceError,
)

try:
    # Code that interacts with the RPLIDAR device
    pass
except RPLidarConnectionError as exc:
    print(f"Connection error: {exc}")
except RPLidarProtocolError as exc:
    print(f"Protocol error: {exc}")
except RPLidarTimeoutError as exc:
    print(f"Timeout error: {exc}")
except RPLidarDeviceError as exc:
    print(f"Device error: {exc}")
except RPLidarError as exc:
    print(f"General RPLIDAR error: {exc}")
```

## Exception Hierarchy
```plaintext
RPLidarError
├── RPLidarConnectionError
|   └── RPLidarTimeoutError
├── RPLidarProtocolError
└── RPLidarDeviceError
```