Version 2.0

Milestone 1
✔ Transport Layer
✔ Transport Tests
✔ Protocol Layer
✔ Protocol Tests
✔ pyproject.toml
✔ Package Structure
✔ Documentation

Milestone 2
□ Driver Layer
    ✔ Implement get_info()
    ✔ Implement get_health()
    ✔ Implement get_samplerate()
    ✔ Implement stop()
    ✔ Implement reset()
    □ Implement start_scan()

□ Driver Tests
□ Hardware Integration
□ Documentation

Milestone 3
□ Live Data Processing
□ Data Processing Tests
□ Point Cloud Generation
□ Point Cloud Tests

Milestone 4
□ Visualization Layer
□ Visualization Tests 

### Concurrent Data Pipeline

- [ ] Establish correct single-threaded streaming
- [ ] Add background acquisition worker
- [ ] Add bounded scan queue
- [ ] Add shutdown event
- [ ] Propagate worker exceptions
- [ ] Define queue overflow policy
- [ ] Measure acquisition and processing rates
- [ ] Evaluate multiprocessing if processing falls behind

□ Incomplete
→ In Progress
✔ Complete
