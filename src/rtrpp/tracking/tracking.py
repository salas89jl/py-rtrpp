import numpy as np
from rtrpp.tracking.track import Track
        
class SimpleTracker:
    # Constructor
    def __init__(
            self,
            max_distance=2.0
    ):
        self.max_distance = max_distance
        self.next_track_id = 0
        self.tracks = {}

    # Calculate the normalized distance between a detection and a track based on their center coordinates
    def distance(
            self,
            detection, 
            track
    ):
        return np.linalg.norm(
            detection.center[:2] - track.center[:2]
        )
    
    # Create a new track for a detection that cannot be associated with any existing tracks
    def create_track(
            self, 
            detection
    ):
        track = Track(
            self.next_track_id,
            detection
        )

        self.tracks[
            self.next_track_id
        ] = track

        self.next_track_id += 1

        return track
    
    # Update the active tracks based on the new detections in the current frame
    def update(self, detections):
        # Create a new dictionary to store the updated tracks and a set to keep track of used track IDs
        updated_tracks = {}
        used_track_ids = set()

        # Iterate through the detections and try to associate them with an existing track based on the distance and classification
        for detection in detections:
    
            best_track_id = None
            best_distance = float("inf") # Initialize the best distance to infinity

            for track_id, track in self.tracks.items():
                # Check if the track ID has already been used in this update cycle
                if track_id in used_track_ids:
                    continue
                # Check if the detection and track are compatible based on their classification
                if not self.compatible(detection, track):
                    continue
                
                # Calculate the distance between the detection and the track
                distance = self.distance(detection, track)

                # Update the best track ID and best distance if the current distance is smaller than the best distance found so far
                if distance < best_distance:
                    best_distance = distance
                    best_track_id = track_id 
            
            # If a compatible track is found within the maximum distance, update the track with the new detection. Otherwise, create a new track for the detection.
            if best_track_id is not None and best_distance <= self.max_distance:
                track = self.tracks[best_track_id]
                track.update(detection)

                updated_tracks[best_track_id] = track
                used_track_ids.add(best_track_id)
            # If no compatible track is found, create a new track for the detection and add it to the updated tracks
            else:
                track = self.create_track(detection)
                updated_tracks[track.track_id] = track
                self.next_track_id += 1
        
        # Update the active tracks with the updated tracks and return the list of active tracks
        self.tracks = updated_tracks

        # Return the list of active tracks
        return list(self.tracks.values())

    # Check if a detection and a track are compatible based on their classification
    def compatible(self, detection, track):
        if detection.classification == track.detection.classification:
            return True
        
        if detection.classification == "Unknown":
            return True
        
        if track.detection.classification == "Unknown":
            return True
        
        return False
    
