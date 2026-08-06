ADR-006: RPLIDAR Driver Layer Buffer Strategy

Decision: 

Implement a buffer strategy in the RPLIDAR driver layer to efficiently manage incoming scan data and ensure timely processing of measurements.

Reason:

    The RPLIDAR sensor generates a continuous stream of scan data that needs to be processed in real-time. Without an efficient buffer strategy, there is a risk of data loss or delayed processing, which can negatively impact the performance and accuracy of the perception system. Implementing a buffer allows the driver to temporarily store incoming data, ensuring that more measurements are available for processing and reducing the likelihood of data loss.

Consequences:

    Negative:
        - Increased memory usage due to the buffer.
        - Potential complexity in managing buffer overflow and ensuring timely processing of data.

    Positive:
        - Reduced risk of data loss.
        - Improved real-time processing of scan data.
        - More consistent availability of measurements for the perception system.

