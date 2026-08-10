# Buffer Notes for Implementation `read_scan()`
Date: 2026-07-20
Prepared by: Jose
Version: 2.0
Purpose: To document the buffer management considerations and implementation details for the `read_scan()` function in the RPLIDAR project.

## What is a buffer?

A buffer is a region of memory that is used to temporarily store data while it is being moved from one place to another. Its main purpose is to act as a holding area that absorbs mismatches in speed, timing, or data transfer size between two different devices or software processes. (Wikipedia).

### Buffers exist everywhere
Buffers are used in a wide variety of everyday applications without one realizing it. For example, when we type on a keyboard, the keystrokes are temporarily stored in a buffer before being processed by the computer. Similarly, when streaming a video or a song from a music player, the data is buffered to ensure smooth playback without interruptions. Another example is when printing documents, the data is often buffered before being sent to the printer to accommodate differences in processing speed between the computer and the printer.

## Why buffers are used

Buffers are essential to modern computing for several reasons:

- **Speed Matching:** Buffers help to match the speed of different devices or processes. For example, they synchronize fast hardware like CPUs with slower devices like hard drives or network interfaces. Therefore, data can be temporarily stored in the buffer until the slower device is ready to process it.
- **Data Integrity:** Buffers support data integrity by allowing partial data to be assembled, validated, and processed before it is consumed. Correct overflow, synchronization, and error-handling policies are still required.. 
- **Handling Data Bursts:** Sometimes devices send or receive data in uneven bursts. Buffers can temporarily store this data, allowing the system to process it at a steady rate without losing information. 
- **Resource Management:** Buffers help manage system resources efficiently by temporarily holding data in memory, reducing the need for frequent access to slower storage devices and minimizing the overhead associated with data transfer.

## Types of Buffers

Buffers are classified based on how they organize data and where they are located in a system's memory hierarchy. Common types of buffers include:

- **Circular Buffer (Ring Buffer):** A circular buffer is a fixed-size buffer that wraps around when it reaches the end, overwriting the oldest data. It is commonly used in situations where continuous data streams need to be processed, such as audio or network data.
- **Linear Buffer:** A linear buffer is a simple, contiguous block of memory (a sequence of data bytes or elements stored in adjacent memory locations) used to store data sequentially. Data is added to the end of the buffer and removed from the beginning, following a first-in, first-out (FIFO) order. In other words, its a queue data structure. A linear buffer stores data sequentially in a contiguous region. When the write position reaches the end, the implementation must reset, compact, resize, or reject additional data. Unlike a circular buffer, it does not automatically wrap around to the beginning.
- **Double Buffer:** A double buffer uses two alternating buffers to hold data. While one buffer is being processed, the other buffer can be filled with new data. For example, while the CPU writes data into one, a device (like a GPU or network interface) can read data from the other. This technique helps prevent visual stuttering and ensures smooth data processing.
- **Memory-Mapped Buffer:** A memory-mapped buffer maps a file or device region into virtual memory. The application accesses the mapped region through memory operations while the operating system manages the underlying I/O and page transfers. This can improve performance for large data sets and enable efficient sharing of data between processes.
- **Input/Output (I/O) Buffer:** An I/O buffer is used to temporarily hold data being transferred between an input/output device and the main memory. It helps to smooth out the differences in speed between the device and the CPU, ensuring efficient data transfer and reducing the likelihood of data loss or corruption.

## Buffer Management Considerations
When managing buffers, one needs to keep several considerations in mind:

- **Buffer Size:** Ensure that the buffer is large enough to accommodate the incoming data stream without overflowing. The size should be chosen based on the expected data rate and the processing speed of the software consuming the data.
- **Buffer Type:** Choose the appropriate type of buffer (e.g., circular, linear, double) based on the data access patterns and the requirements of the application. Circular buffers are often preferred for continuous data streams to efficiently manage memory and avoid overflow.
- **Buffer Management:** Implement strategies to handle buffer overflow and underflow conditions. This may include discarding old data, pausing data acquisition, or dynamically resizing the buffer based on the current data rate and processing speed.
- **Buffer Monitoring:** Continuously monitor the buffer usage to detect potential overflow or underflow situations early. This can help in taking corrective actions before data loss occurs.
- **Buffer Flushing:** Implement mechanisms to flush the buffer when necessary, such as when starting a new scan or when recovering from an error condition. This ensures that stale or corrupted data does not affect subsequent measurements.
- **Buffer Synchronization:** Ensure that the buffer is properly synchronized with the incoming data stream, especially when dealing with partial scans or when resuming data acquisition after a pause. This helps maintain data integrity and prevents misalignment of measurements.
- **Buffer Debugging:** Implement logging or debugging mechanisms to track buffer usage and identify potential issues during development and testing. This can aid in diagnosing problems related to buffer management and optimizing performance.
- **Buffer Documentation:** Maintain clear documentation of the buffer architecture, including its size, type, and management strategies. This helps new developers understand the system and ensures consistent handling of buffers across the project.
- **Buffer Testing:** Develop comprehensive tests to validate the buffer's behavior under various conditions, such as high data rates, partial scans, and error scenarios. This ensures the reliability and robustness of the buffer management system.

## Buffers in the RPLIDAR Project

In the RPLIDAR project, the driver has several layers of interaction with the hardware and software components:

```text
RPLIDAR
↓
UART transmitter
↓
USB-to-Serial adapter buffer
↓
Operating-system serial receive buffer
↓
pyserial receive buffer
↓
Transport/driver reads
↓
Application scan buffer
↓
Processing and visualization
```

Each of these different layers may have their own buffers to temporarily store data as it moves between the hardware and software components. 

### __RPLIDAR__
Although the exact implementation details are currently not publicly documented, the RPLIDAR likely has an internal buffer in order to allow the microcontroller to continue acquiring measurements while the UART hardware shifts bytes out at the configured baud rate. However, from the perspective of the host computer, this buffer is not directly accessible, thus, from the driver's perspective the RPLIDAR behaves like a continuously streaming device once the scanning starts.

Since, the RPLIDAR continuously streams data once scanning starts, it is crucial to have buffers at various layers of the software stack to temporarily store this incoming data. These buffers help manage the differences in data processing speeds between the RPLIDAR hardware, the USB driver, the Pyserial library, and the higher-level driver functions, ensuring smooth and reliable data acquisition.

__For Example__:
The RPLIDAR does not wait for the until an entire scan is completed before sending data, while it is in standard mode. Instead, the device begins to transmit measurements packets immediately. It does not wait until it has collected a 360 degree revolution. Instead, it sends data continuously like this:

```text
Angle 0.2°
↓

Packet

Angle 0.6°
↓

Packet

Angle 1.1°
↓

Packet

Angle 1.5°
↓

Packet

...
```
This means that the first packet of data that may be received by the driver may not have a start flag indicating the beginning of a new scan. And, eventually, a packet with a start flag will be received, indicating the beginning of a new scan.
```text
...
358.8°
359.2°
359.8°
0.1°   <-- Start flag
0.5°
1.0°
...
```

Therefore, the driver must be able to handle partial scans and correctly assemble the incoming packets into complete scan data using its internal buffers.

### __USB and Operating-System Buffers__
The USB and operating-system layers introduce additional buffers that temporarily store the received bytes before they are processed by the driver. This means that when the RTRPP program calls:
```python
   transport.read(5)
```
those five bytes may already be waiting in the operating-system buffer. That is why reading from the serial port does not necessarily correspond to the actual arrival of receiving bytes directly from the RPLIDAR sensor at that exact instant. The bytes may have arrived slightly earlier. 

### __Application-Level Buffers__

Application-level buffers are used by the driver and higher-level software components to temporarily store measurements as they are received from the RPLIDAR. For example, `read_scan()` uses an internal buffer to accumulate measurements until a complete scan is available. Using the `iter_measurements()`:

```python
def iter_measurements(self) -> Iterator[RPLidarScanData]:
    while self.scanning_state._is_scanning:
        yield self._read_measurement()
```
```python
def read_scan(self) -> list[RPLidarScanData]:
    scan = []
    for measurement in self.iter_measurements():
        scan.append(measurement)
        if measurement.start_flag and scan:
            break
        
    return scan
```
Here the `read_scan()` consumes measurements from iter_measurements() and stores them in a scan-level list buffer until a complete revolution has been assembled. However, it is important to note that this implementation assumes that `read_scan()` correctly handles partial reads and maintains the integrity of the measurement stream.


### Why buffer management is important for this sensor
The RPLIDAR S2L is capable of producing data very quickly. According to the S2L datasheet, the device has a 1 Mbps serial interface, and the standard scan response consists of five-byte packets. At 1 Mbps UART using 8-N-1 structural arrangement of bits used to enclose and transmit a single byte of data:
```text
1  start bit
8  data bits
1  stop bit
---------
10 bits per byte
```
Therefore, for each byte transmitted over the UART interface, a total of 10 bits are sent, including the start bit, the 8 data bits, and the stop bit.

The approximate maximum byte throughput of the UART interface can be calculated as follows:

```text
1 Mbps / 10 bits per byte = 100,000 bytes per second
```

This means that the UART interface can theoretically transmit up to 100,000 bytes per second. Given that the RPLIDAR S2L produces five-byte packets for each measurement in standard scan mode, the maximum number of measurements per second can be estimated as follows:

```text
100,000 bytes per second / 5 bytes per measurement ≈ 20, 000 measurements per second
```

Using the measured standard sample rate of 62 microseconds for the RPLIDAR S2L, retrieved using the `get_samplerate()` method, the maximum number of measurements per second can be calculated as follows:

```text
1 second / 62 microseconds per measurement ≈ 16,129 measurements per second
```
This indicates the standard stream can occupy a substantial portion of the available UART bandwidth. The stream rate can be calculated as follows:

```text
16,129 measurements per second * 5 bytes per measurement = 80,645 bytes per second
```

This shows that the standard stream uses approximately 80% of the maximum UART throughput, leaving limited headroom for additional data or potential transmission delays. Meaning, the acquisition code should promptly read the incoming data and avoid any unnecessary work between each read.

## The problem buffers solves

Imagine that a sensor steadily sends data:
```
packet packet packet packet packet ...
```

Suppose the application occasionally pauses to render an Open3D frame, run clustering algorithms, perform tracking, or write a file. During these pauses, bytes will continue to arrive from the sensor, and potentially accumulate in the operating-system buffer.

```
Sensor:
P1 P2 P3 P4 P5 ...

Application:
read P1
processing...
processing...
processing...

OS buffer:
P2 P3 P4 P5 ...
```

A short pause can be acceptable because the operating-system buffer can temporarily hold incoming data. But, a prolonged pause can fill the buffer completely:

```
OS buffer full
 ↓
new serial bytes arrive
 ↓
old or new bytes may be lost
 ↓
 packet alignment is damaged
```
Note, that once the bytes are lost or the packet alignment is damaged, the application may receive incomplete or corrupted scan data, which can affect the accuracy and reliability of the measurements.



One important strategy to mitigate this issue is to implement an internal buffer within the transport or the driver layer's `_read_exactly()` method. The internal byte buffer handles differences between serial-read boundaries and protocol-packet boundaries. It does not prevent operating-system buffer overflow. The acquisition loop must still read quickly enough to avoid losing incoming bytes from the sensor.

#### Packet boundaries vs stream boundaries

Serial communication is a byte stream, meaning that data is transmitted as a continuous sequence of bytes without inherent packet boundaries. This implies that it does not intrinsically preserve for instance a five-packet boundary, and the application must rely on its own logic to correctly assemble and interpret the incoming data into complete packets.

The sensor may send:
```text
[A B C D E]
[F G H I J]
[K L M N O]
...
```
While the serial reads might return:
```text
read 1: [A B C]
read 2: [D E F G]
read 3: [H I J K L]
...
```
The stream is still correct, but the grouping of bytes returned by the read() does not necessarily align with the original packet boundaries. Therefore, the application must correctly reassemble the bytes into complete packets based on its own logic.

## Two useful buffering levels for RTRPP project

1. Raw-byte buffering:
   
   
   Example implementation:

   ```python
   class Driver:
       def __init__(self):
           self._internal_buffer = bytearray()

    def _read_exactly(
        self,
        size: int,
        operation: str,
    ) -> bytes:
        while len(self._internal_buffer) < size:
            remaining = size - len(self._internal_buffer)
            chunk = self._transport.read(remaining)

            if not chunk:
                raise RPLidarTimeoutError(
                    f"{operation} expected {size} bytes, "
                    f"but only {len(self._internal_buffer)} "
                    "bytes were received."
                )

            self._internal_buffer.extend(chunk)

        result = bytes(self._internal_buffer[:size])
        del self._internal_buffer[:size]

        return result
   ```

   This approach ensures that even if the serial reads return partial packets, the application will always receive complete packets, maintaining data integrity and alignment.

   Alternatively, one could implement the raw-byte buffer in the transport layer itself, similar to how it is done in the `RPLidarTransport` class. This would centralize the buffering logic and ensure that all reads from the transport are properly aligned and complete, reducing the risk of data loss or misalignment at the application level.

2. Packet-level buffering:
   
   __Measurement Data Buffering__:
    The responsibility of this buffer is to store complete packets of measurement data, ensuring that the application can retrieve a complete packet whenever it needs one, without worrying about partial reads or misaligned data. Possible locations where this buffer could be implemented include the `driver.read_scan()` or a scan assemble class that would be responsible for constructing complete scans from the raw packets.

   Example implementation:

   We can keep the boundary measurement for the next call 

   ```python
   class Driver:
       def __init__(self):
           self._transport = transport
           self._pending_measurement: prot.RPLidarScanData | None = None
   ```
   Then, implemented in the `read_scan()`:

   ```python
   def read_scan(self) -> list[prot.RPLidarScanData]:
       """ Return one complete revolution."""
        # Start with an empty scan and include any pending measurement from the previous call.
        scan: list[prot.RPLidarScanData] = []
        
        # If there is a pending measurement from the previous call, include it at the start of the scan.
        if self._pending_measurement is not None:
            scan.append(self._pending_measurement)
            self._pending_measurement = None

        # Iterate over new measurements and build the current scan.
        for measurement in self.iter_measurements():

            # Check if the current measurement indicates the start of a new scan and if the current scan already has measurements.
            if measurement.start_flag and scan:
                self._pending_measurement = measurement
                break
            scan.append(measurement)
        
        return scan
```
Now when `read_scan()` is called:
```text
read_scan() call 1: A0 A1 A2 A3 ...

Pending: B0

read_scan() call 2: B0 B1 B2 B3 ...

Pending: C

And so on for subsequent calls, with each call including any pending measurement from the previous call at the start of the scan.
```

However, there is another boundary issue that remains. Specifically, if `read_scan()` begins its reading in the middle of a revolution. Lets say that the first packet read is partway through a revolution and the following packet sequence are read:

```text
A149
A150
A151
...
B0 <-> start of new scan
B1
B2
...
C0
C1
C2
...
```
With a simple implementation like the one described above, the first incomplete revolution (A149, A150, A151, ...) would be returned by the `read_scan()` call. 

A possible improvement to handle this situation is to implement is to wait for the next start of a new scan before iterating over and collecting measurements to acquire a more complete revolution.

```python
def _wait_for_new_scan(self) -> prot.RPLidarScanData:
    """Wait for start of new scan and return the first measurement of the new scan."""
    for measurement in self.iter_measurements():
        if measurement.start_flag:
            return measurement
    # If no start_flag is found, raise an exception or handle it appropriately.
    raise RuntimeError("Scanning stopped before a scan boundary was found.")
```

Now, before starting to collect measurements for a new scan in the `read_scan()` method, we can call `_wait_for_new_scan()` to ensure that we begin at the start of a new scan. 

```python
def read_scan(self) -> list[prot.RPLidarScanData]:
    scan: list[prot.RPLidarScanData] = []

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

    return scan
```
Now, when `read_scan()` is called, it will always start at the beginning of a new scan, ensuring that the returned scan is as complete as possible and avoiding the issue of starting in the middle of a revolution.

## Buffering for Live Processing

Eventually, as the system evolves to support visualization and real-time processing of scan data, it will be necessary to implement buffering strategies that allow for efficient access. The project architecture could perhaps look something like this:

```text
Acquisition Thread -> bounded scan queue -> Processing Thread -> Visualization Thread
```

For example, the use of a `Queue` from the `queue` module in Python can help implement a bounded scan queue, allowing the acquisition thread to push complete scans into the queue while the processing thread consumes them at its own pace.

```python
from queue import Queue

scan_queue: Queue[list[prot.RPLidarScanData]] = Queue(maxsize=3)


# Publish the latest scan to the bounded scan queue, discarding the oldest if necessary.
def publish_latest_scan(
    scan: list[prot.RPLidarScanData],
) -> None:
    try:
        scan_queue.put_nowait(scan)
        return
    except Full:
        pass

    try:
        scan_queue.get_nowait()
    except Empty:
        pass

    try:
        scan_queue.put_nowait(scan)
    except Full:
        # Another producer filled it first.
        pass


# Acquisition thread
def acquisition_thread(driver: Driver):
    while True:
        scan = driver.read_scan()
        scan_queue.put(scan)


# Processing thread
def processing_thread():
    while True:
        scan = scan_queue.get()
        process_scan(scan)
```

### Why Use a Bounded Scan Queue

Using an unbounded scan queue can lead to excessive memory usage if the processing thread cannot keep up with the acquisition thread. By using a bounded scan queue, we can apply backpressure to the acquisition thread, ensuring that the system remains responsive and memory usage stays within reasonable limits. For instance, if an unbounded queue is used:
```text
Sensor produces: 10 scans/sec
Processing thread can handle: 6 scans/sec

Backlog grows indefinitely:
4 scans after a 1 second
40 scans after 10 seconds
400 scans after 100 seconds
... and so on, leading to potentially unbounded memory usage.
```
This means that memory consumption grows, latency increases, and visualization displays would show increasingly outdated information, making real-time processing ineffective.

In real-time robotics applications, old scans are usually less valuable than recent scans. A common real-time policy is to discard old scans when the queue is full, and always keep the most recent scans for processing and visualization.

```python
# Acquisition thread with bounded queue
def acquisition_thread(driver: Driver):
    while True:
        scan = driver.read_scan()
        if scan_queue.full():
            scan_queue.get()  # Discard the oldest scan
        scan_queue.put_nowait(scan)  # Non-blocking put, raises queue.Full if the queue is full
```

However, for offline recording, it is usually desirable to keep all scans, even if the processing thread cannot keep up in real-time. In this case, an unbounded queue or a large enough bounded queue can be used to store all scans for later processing and analysis.

  

## Different Buffering Policies 

| Scenario | Buffering Policy | Good For | Risks |
|----------|-----------------|----------|-------|
| Lossless recording | Never discard data <br> Producer waits if necessary| • Dataset recording <br> • Debugging <br> • Reproducible experiments | • Acquisition may fall behind <br> • OS serial buffers may overflow |
| Real-time processing | Bounded queue with discard oldest policy | • Responsive visualization <br> • Low latency processing | • Some scans may be lost if processing cannot keep up |
| Batch processing | Large bounded queue or unbounded queue | • Efficient offline processing <br> • Analysis of large datasets <br> • Motion estimation | • High memory usage if acquisition rate is high |


## Buffers in the driver
The driver should be designed with relatively small internal buffers to avoid excessive memory usage, and should handle serial communication such as packets, measurements, and one revolution. While the application or acquisition layers should handle higher-level buffering and processing such as multiple revolutions: queues, recording, dropped-frames policy, and other strategies to ensure efficient and reliable data handling.

This design separation ensures that the driver remains lightweight and focused. A potential structure could be:

```text
Transport
    Raw serial reads

Driver
    Small internal buffers
    Handles packets, measurements, and one revolution assembly

Acquisition Layer
    Handles background reading
    Manages scan queues and buffering for processing

Processing Layer
    Consumes scans from acquisition layer
    Performs real-time processing and analysis such as:
     Filtering, Conversions, Tracking

Visualization Layer
    Consumes processed scans from processing layer
    Handles real-time visualization and user interaction

Recording Layer
    Consumes scans from acquisition layer
    Stores scans for offline analysis and replay

``` 

