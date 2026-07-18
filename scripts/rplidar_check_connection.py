# This script checks the connection to the RPLidar device.


from rtrpp.sensors.rplidar.transport import RPLidarTransport


def main():
    port = ""  # Replace with your RPLidar port
    lidar = RPLidarTransport(port)

    try:
        lidar.open()
        if lidar.is_open:
            print(f"Connected: {lidar.is_open}")
        else:
            print("Failed to connect to RPLidar.")
    finally:
        lidar.close()
        print("Connection closed.")


if __name__ == "__main__":
    main()
