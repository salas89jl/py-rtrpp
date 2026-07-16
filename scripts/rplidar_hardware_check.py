from rtrpp.sensors.rplidar.driver import RPLidarDriver
from rtrpp.sensors.rplidar.exceptions import RPLidarError
from rtrpp.sensors.rplidar.transport import RPLidarTransport

import pytest

def main() -> None:
    port = "/dev/tty.usbserial-210"
    transport = RPLidarTransport(
        port=port,
        baudrate=1_000_000,
    )

    try:
        transport.open()
        driver = RPLidarDriver(transport)

        # Execute commands sequentially
        driver.stop()
        info = driver.get_info()
        health = driver.get_health()
        sample_rate = driver.get_samplerate()   
        
        print(info)
        print(health)
        print(sample_rate)
    except RPLidarError as exc:
        print(f"RPLIDAR integration test failed: {exc}")
        raise

    finally:
        transport.close()
        if not transport.is_open:
            print("Serial connection is successfully closed. ")


if __name__ == "__main__":
    main()

