import numpy as np

class Track:
    # Constructor
    def __init__(self, track_id, detection):
        
        self.track_id = track_id
        
        self.detection = detection

        self.center = detection.center

        self.length = detection.length
        self.width = detection.width
        self.height = detection.height
        self.speed = 0.0
        self.avg_speed = 0.0

        self.history = [
            detection.center
        ]

        self.frames_seen = 1
    # Update the track attributes based on the new detection and increment the frames_seen counter
    def update(self, detection):
        self.detection = detection
        self.center = detection.center
        self.length = detection.length
        self.width = detection.width
        self.height = detection.height

        self.history.append(detection.center)

        self.speed = self.compute_velocity()
        self.avg_speed = self.compute_average_velocity()        

        self.frames_seen += 1

    def compute_velocity(
            self, 
            dt=0.1
    ):  
        """
        Compute the instantaneous velocity of the track based on the last two center positions in the history.

        Parameters:
            dt (float): The time interval between frames in seconds.

        Returns:
            float: The instantaneous velocity of the track in meters per second.
        """
        # Check if there are at least two center positions in the history to compute velocity
        if len(self.history) < 2:
            return 0.0
        
        # Retrieve the last two center positions from the history
        previous_center = self.history[-2]
        current_center = self.history[-1]

        # Using only x and y from each of the center calculate displacement
        displacement = np.linalg.norm(
            current_center[:2] - previous_center[:2]
        )
        
        # Return calculated instantaneous velocity as displacement over time
        return displacement / dt

    def compute_average_velocity(
            self, 
            dt=0.1
    ):
        """
        Compute the average velocity of the track based on the center positions in the history.

        Parameters:
            dt (float): The time interval between frames in seconds.

        Returns:
            float: The average velocity of the track in meters per second.
        """
        
        if len(self.history) < 2:
            return 0.0
        
        total_displacement = 0.0

        # Compute the total displacement over all frame-to-frame displacements
        for i in range(1, len(self.history)):
            previous_center = self.history[i - 1]
            current_center = self.history[i]
            displacement = np.linalg.norm(current_center[:2] - previous_center[:2])
            total_displacement += displacement

        # Calculate total time elapsed based on number of frames
        total_time = (len(self.history) - 1) * dt

        # Calculate average velocity as total displacement over total time
        average_velocity = total_displacement / total_time
        
        return average_velocity
    
    def speed_mph(self):
        return self.speed * 2.23694
    
    def ave_speed_mph(self):
        return self.ave_speed_mph * 2.23694
    
    def __str__(self):
        return (
            f"Track {self.track_id} | "
            f"{self.detection.classification} | "
            f"Speed={self.speed:.2f} m/s | "
            f"Avg Speed={self.avg_speed:.2f} m/s | "
            f"History {len(self.history)}"
        )