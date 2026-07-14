class RPLidarError(Exception):
    """Base exception for all RPLIDAR-related failures."""

class RPLidarConnectionError(RPLidarError):
    """Raised when communication with the RPLIDAR fails."""

class RPLidarProtocolError(RPLidarError):
    """Raised when received data violates the RPLIDAR protocol."""

class RPLidarTimeoutError(RPLidarConnectionError):
    """Raised when an expected RPLIDAR response is not received within the specified timeout period."""

class RPLidarDeviceError(RPLidarError):
    """Raised when the RPLIDAR device reports an internal error or malfunction."""