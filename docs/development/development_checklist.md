# Version 2.0 Development Checklist

**Current milestone:** Milestone 3 – Hardware Integration

**Current branch:** feature/rplidar-interface

**Latest milestone completed:** Milestone 2

**Unit tests:** 75 passing

__Milestone 1__
Communication Foundation
- [x] Transport Layer
- [x]  Transport Tests
- [x]  Protocol Layer
- [x]  Protocol Tests
- [x]  pyproject.toml
- [x]  Package Structure
- [x]  Documentation

__Milestone 2__
High-level Driver
- [x]  Driver Layer (w/o start_scan())
  - [x]  Implement get_info()
  - [x]  Implement get_health()
  - [x]  Implement get_samplerate()
  - [x]  Implement stop()
  - [x]  Implement reset()
- [x]  Driver Tests (w/o start_scan())
  - [x]  Implement get_info() tests
  - [x]  Implement get_health() tests
  - [x]  Implement get_samplerate() tests
  - [x]  Implement stop() tests
  - [x]  Implement reset() tests
- [x]  Exception hierarchy
  - [x]  Implement RPLidarError (base exception)
  - [x]  Implement RPLidarCommunicationError (communication error)
  - [x]  Implement RPLidarProtocolError (protocol error)
  - [x]  Implement RPLidarTimeoutError (timeout error)
  - [x]  Implement RPLidarDeviceError (device error)
- [x]  Documentation
  - [x] Add driver layer documentation
  - [x] Add driver layer tests documentation
  - [x] Add exception hierarchy documentation


__Milestone 3__
Hardware Integration
- [ ] Hardware Communication Verification
  - [x] Serial port opened successfully
  - [x] Verify `get_info()` returns plausible values
  - [x] Verify `get_health()` reports a recognized status
  - [x] Verify `get_samplerate()` return plausible timing values
  - [x] Verify `stop()` completes without communication failure
  - [x] Verify reset()
  - [x] Verify transport closes even when command fails
  - [x] Hardware results are recorded in documentation
  - [x] Existing 75 unit tests pass with hardware connected
- [ ] Driver Layer (w/ start_scan feature)
  - [ ] Implement start_scan()
  - [ ] Implement stop_scan()
  - [ ] Verify continuous scan data acquisition
- [ ] Driver Tests (w/ start_scan feature)
  - [ ] Implement start_scan() tests
  - [ ] Implement stop_scan() tests
- [ ] Documentation
  - [ ] Add driver layer scan features documentation
  - [ ] Add driver layer scan features tests documentation

__Milestone 4__
Live Data Processing
- [ ] Documentation
- [ ] Implement live data processing pipeline
  - [ ] Aquire scan packets
  - [ ] Decode scan packets
  - [ ] Convert polar coordinates to cartesian coordinates
  - [ ] Generate point cloud
  - [ ] Verify point cloud generation
- [ ] Data Processing Tests
- [ ] Point Cloud Generation
- [ ] Point Cloud Tests

__Milestone 5__
Visualization Layer
- [ ] Documentation
- [ ] Open3D Visualization
- [ ] Live point cloud updates
- [ ] Camera control
- [ ] Performance measurements
- [ ] Visualization Tests

__Milestone 6__
Application Layer
- [ ] Documentation
- [ ] Configuration
- [ ] Logging
- [ ] CLI
- [ ] Run-time Parameters
- [ ] Save/Load Scan Data

__Milestone 7__

- [ ] Establish correct single-threaded streaming
- [ ] Add background acquisition worker
- [ ] Add bounded scan queue
- [ ] Add shutdown event
- [ ] Propagate worker exceptions
- [ ] Define queue overflow policy
- [ ] Measure acquisition and processing rates
- [ ] Evaluate multiprocessing if processing falls behind


