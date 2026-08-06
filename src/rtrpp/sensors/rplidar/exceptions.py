class RPLidarError(Exception):
    """Base exception for all RPLIDAR-related failures."""

    pass


class RPLidarConnectionError(RPLidarError):
    """Raised when communication with the RPLIDAR fails."""

    pass


class RPLidarProtocolError(RPLidarError):
    """Raised when received data violates the RPLIDAR protocol."""

    pass

class RPLidarDeviceError(RPLidarError):
    """Raised when the RPLIDAR device reports an internal error or malfunction."""

    pass

class RPLidarHealthError(RPLidarDeviceError):
    """Raised when the RPLIDAR reports a health status indicating a problem."""

    pass

class RPLidarTimeoutError(RPLidarConnectionError):
    """Raised when expected RPLIDAR response is not received within the specified timeout period."""

    pass

class RPLidarDriverError(RPLidarError):
    """Raised when the RPLIDAR driver encounters an error."""

    pass

class RPLidarStateError(RPLidarDriverError):
    """Raised when the RPLIDAR is in an unexpected or invalid state."""

    pass

class TransportError(Exception):
    """Base exception for transport failures."""

    pass


class TransportTimeoutError(TransportError):
    """Requested serial bytes were not received before timeout."""

    pass    


class TransportConnectionError(TransportError):
    """The underlying serial connection failed."""

    pass