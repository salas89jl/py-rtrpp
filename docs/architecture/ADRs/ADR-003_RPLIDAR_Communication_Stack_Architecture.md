ADR-003: Communication Stack Architecture for RPLIDAR Integration

Context:

The RPLIDAR integration requires a well-defined communication stack architecture to facilitate a reliable and efficient interaction between the software components and the RPLIDAR device. 

Decision:


The RPLIDAR integration will be structured into a layered communication stack consisting of the following layers:
1. Transport Layer: Responsible for handling the low-level communication with the RPLIDAR device, including opening and closing the serial connection, sending and receiving raw data, and managing timeouts and errors.
2. Protocol Layer: Responsible for implementing the RPLIDAR communication protocol, including encoding and decoding commands and responses, validating response descriptors, and handling protocol-specific errors.
3. Driver Layer: Responsible for providing a high-level interface for interacting with the RPLIDAR device, including sending commands, receiving responses, and managing the device state. This layer will abstract the underlying transport and protocol layers, providing a simplified API for other components of the system to interact with the RPLIDAR device.

Reason:

The layered architecture provides a clear separation of concerns, allowing for easier maintenance, testing, and future enhancements. Each layer can be developed and tested independently, and changes in one layer will have minimal impact on the other layers.

Consequences:

Possitive Consequences:
  
- Each layer can be developed and tested independently.
- Protocol parsing does not require hardware access, allowing for easier testing and debugging.
- Driver tests can be performed without requiring a physical RPLIDAR device, enabling faster development and testing cycles.
- Alternative transport implementations can be easily integrated without affecting the higher-level layers, providing flexibility for future enhancements.

Negative Consequences:

- More complex module structure, which may require additional effort to understand, maintain, and navigate the codebase.
- Errors must be translated between layers, which may introduce additional complexity and potential for miscommunication between layers.
- Integration requires careful coordination between layers to ensure that the overall system functions correctly and efficiently.

Alternatives Considered:

Monolithic Architecture: A single layer that handles all aspects of communication with the RPLIDAR device, including transport, protocol, and driver functionality. This approach would simplify the module structure but would make testing and maintenance more difficult, as changes in one area could have unintended consequences in other areas.
