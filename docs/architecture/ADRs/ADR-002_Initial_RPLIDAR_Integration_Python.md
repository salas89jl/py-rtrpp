ADR-002: Use Python for initial RPLIDAR integration

Decision:
Use Python for initial hardware validation and live scan aquisition. 

Reason:
RTRPP is currently Python-based, and the early milestones prioritize communication validation, data interpretation, and integration over low-level performance optimization. 

Future Considerations:
C++ may be used for future lower-level driver work, ROS 2 integration, or other performance-critical applications.

