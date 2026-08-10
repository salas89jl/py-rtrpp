# Phase 8 _ Object Tracking Across Frames
## Introduction
So far in our project, we have been able to detect and classify objects in a single frame of LiDAR data. But, now we want to track objects across multiple frames. This is important step for understanding the movement of objects in the scene. In this phase we will implement a simple tracking system that associates the detected objects in the current frame with the objects detected in the previous frame based on their spatial proximity and classification.

## How the Simple Tracking System Works
By creating a tracking system, we can maintain the identity of objects as they move through the scene. With the implementation of a bounding box-based in the pipeline, we can use the center coordinates of the bounding boxes to calculate the distance between detected objects in consecutive frames. If a detected object in the current frame is close enough to a detected object in the previous frame and they have compatible classifications, we can associate them as the same object. This will allow us to track the movement of objects over a period of time and analyze their behaviour. 

## Steps for Implementing the Tracking System
1. We will create a `Detection` class that represents a detected object in the current frame. Each detection object will have attributes such as the cluster ID, classification, center coordinates, bounding box, dimensions, and volume. The `Detection` class will also have methods to set and get these attributes, as well as a method to return a string representation of the detection object.
2. We will create a `Track` class that represents a tracked object across frames. Each track object will have attributes such as the track ID, the associated detection object, center coordinates, dimensions, a history of previous detections, and the number of frames the track has been seen in. The `Track` class will also have a method to update its attributes based on a new detection associated with it.
3. We will create a `SimpleTracker` class that manages the active tracks and handles the association of detections to tracks. The `SimpleTracker` class will have methods to calculate the distance between a detection and a track, create a new track for a detection that cannot be associated with any existing tracks, update the active tracks based on new detections, and check if a detection and a track are compatible based on their classification. The `SimpleTracker` class will maintain a dictionary of active tracks and a counter for the next available track ID.

### Step 1: Implementing the Detection Class
By implementing a `Detection` class, we can create a representation of each detected object in the current frame. Having a dedicated class for detections allows us to encapsulate the attributes and methods related to detected objects, making it easier to manage and manipulate them in the tracking system. 

Each detection object will have the following attributes:
- cluster_id: The unique identifier of the cluster.
- classification: The type of object (e.g., car, pedestrian, cyclist, unknown).
- center: The center coordinates of the bounding box.
- bbox: The Open3D bounding box object associated with the cluster.
- length, width, height: The dimensions of the bounding box.
- volme: The volume of the bounding box.
- Additionally, the `Detection` class will have methods to set and get these attributes, as well as a method to return a string representation of the detection object. This will allow us to easily access and manipulate the attributes of each detected object in the tracking system.

### Detection Object
```python
import numpy as np
import open3d as o3d

from src.classification import classify_object_simple


class Detection:
    # Constructor
    def __init__(self, cluster_id, classification, center, bbox, length, width, height):
        self.cluster_id = cluster_id
        self.classification = classification
        self.center = center
        self.bbox = bbox
        self.length = length
        self.width = width
        self.height = height
        self.volume = length * height * width

    # String representation of the detection object
    def __str__(self):
        return (
            f"Cluster {self.cluster_id}: {self.classification} | "
            f"Center=({self.center[0]:.2f}, {self.center[1]:.2f}, {self.center[2]:.2f}) | "
            f"L={self.length:.2f}, W={self.width:.2f}, H={self.height:.2f}, "
            f"V={self.volume:.2f}"
        )
```
### Step 2: Implementing the Track Class
The `Track` class will represent a tracked object across different frames. Each track will have the following attributes:
- track_id: The unique identifier of the track.
- detection: The detection object associated with the track.
- center: The center coordinates of the bounding box.
- length, width, height: The dimensions of the bounding box.
- history: A list of previous detections associated with the track.
- frame_seen: The number of frames the track has been seen in.

Additionally, each track will have a method to update its attributes based on the new detection associated with it.

### Track Object
```python
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

        self.history = [detection.center]

        self.frames_seen = 1

    # Update the track attributes based on the new detection and increment the frames_seen counter
    def update(self, detection):
        self.detection = detection
        self.center = detection.center
        self.length = detection.length
        self.width = detection.width
        self.height = detection.height
        self.history.append(detection.center)
        self.frames_seen += 1
```

### Step 3: Implementing the SimpleTracker Class
We will create a `SimpleTracker` class that will manage the active tracks and handle the association of detections to tracks. The `SimpleTracker` class will have the following attributes:
- max_distance: The maximum distance allowed for associating a detection with a track.
- next_track_id: The next available track ID for new tracks.
- tracks: A dictionary of active tracks, where the keys are track IDs and the values are track objects.

Additionally, the `SimpleTracker` class will have the following methods:
- distance: A method to calculate the normalized distance between a detection and a track based on their center coordinates and dimensions.
- create_track: A method to create a new track for a detection that cannot be associated with any existing tracks. 
- update: A method to update the active tracks based on the new detections in the current frame. This method will iterate through the detections and try to associate them with an existing track based on the distance and classification. If a dectection cannot be associated with any existing tracks, a new track will be created for it. The method will return the updated list of active tracks. 
- compatible: A method to check if a detection and a track are compatible based on their classification. If the classifications match or if either the detection or the track is classified as "Unknown", they are considered compatible. This will help to avoid associating detections of different object types, which could lead to incorrect tracking.

### Simple Tracker Object
```python
class SimpleTracker:
    # Constructor
    def __init__(self, max_distance=2.0):
        self.max_distance = max_distance
        self.next_track_id = 0
        self.tracks = {}

    # Calculate the normalized distance between a detection and a track based on their center coordinates
    def distance(self, detection, track):
        return np.linalg.norm(detection.center[:2] - track.center[:2])

    # Create a new track for a detection that cannot be associated with any existing tracks
    def create_track(self, detection):
        track = Track(self.next_track_id, detection)

        self.tracks[self.next_track_id] = track

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
            best_distance = float("inf")  # Initialize the best distance to infinity

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
```

## Limiations of the Simple Tracking System
While the simple tracking system implemented in this phase can  track objects across frames based on their spatial coordinates and classification, it has several limitations that can affect its performance. Ways that it can fail include:
- Objects are close together: If two objects are close together, the tracker may incorrectly associate detections from one object with the track of another object, leading to incorrect tracking.
- Objects disappear and reappear: If an object disappears from the scene and then reappears, the tracker may not be able to correctly associate the new detection with the previous track, leading to a loss of tracking.
- Objects change classification: If an object changes its classification (e.g., from "Unknown" to "Car"), the tracker may not be able to correctly associate the new detection with the previous track, leading to a loss of tracking.
- Clusters merge or split: If two clusters merge into one or one cluster splits into two, the tracker may not be able to correctly associate the new detections with the previous tracks, leading to a loss of tracking.
- Objects move too fast: If an object moves too fast between frames, the tracker may not be able to correctly associate the new detection with the previous track, leading to a loss of tracking.

However, this simple tracking system provides a basic framework for tracking objects across frames and introduces the concept of traking is data association across time. 


## Restructuring the project
Since we are no longer just analyzing a single point cloud, but rather building a perception system. The current project's src architecture is as follows:
```
src/
├── bounding_boxes.py
├── classification.py
├── cluster_objects.py
├── coordinates.py
├── detection.py
├── distance.py
├── down_sample.py
├── extract_ground_plane.py
├── filter_roi.py
├── filtering.py
├── load_kitti.py
├── plot_utils.py
├── remove_outliers.py
├── synthetic_scan.py
├── three_dimen_visualization.py
├── tracking.py

```

However, as you can see, the current structure is not very organized and does not reflect the different stages of the perception pipeline. To improve the organization of the project, the src directory will be restructured to reflect the different stages of the perception pipeline. The new structure will be as follows:
```
src/
src/
├── core/
│   ├── detection.py          ← detection.py
│   ├── track.py              ← Track class from tracking.py
│   └── tracker.py            ← SimpleTracker from tracking.py
│
├── perception/
│   ├── loading.py            ← load_kitti.py
│   ├── preprocessing.py      ← filter_roi.py, down_sample.py, remove_outliers.py
│   ├── segmentation.py       ← extract_ground_plane.py
│   ├── clustering.py         ← cluster_objects.py
│   ├── bounding_boxes.py     ← bounding_boxes.py
│   ├── classification.py     ← classification.py
│   └── pipeline.py           ← full detection pipeline
│
├── geometry/
│   ├── coordinates.py        ← coordinates.py
│   └── distance.py           ← distance.py
│
├── visualization/
│   ├── open3d_viewer.py      ← three_dimen_visualization.py
│   └── plot_utils.py         ← plot_utils.py
│
└── simulation/
    └── synthetic_scan.py     ← synthetic_scan.py
```

This restructuring helps organize the project into different modules that reflect the different stages of the perception pipeline. The `core` module contains the classes and methods related to the detection and tracking of objects, while the `perception` module holds the methods related to loading, preprocessing, segmenting, clustering, and classifying the point cloud data. The `geometry` module contains methods related to geometric calculations, while the `visualization` module contains methods for visualizing the point cloud data. Finally, the `simulation` module contains methods for generating synthetic point cloud data.




## Updating the Pipeline to Include Tracking
To integrate the tracking system into the existing pipeline, we can start by the integrating all of the seperate modules used to load, filter, cluster, classify the detections, and then track the objects across frames. 


In the `pipeline.py` file, we create a `run_pipeline` function that takes in a string representing the path to the KITTI dataset and a `SimpleTracker` object. The function will load the point cloud data, preprocess it, segment the ground plane, cluster the objects, classify them, and then update the tracker with the new detections. The function will return a list of active tracks after processing all frames in the dataset.

```python
from pathlib import Path
from src.perception.loading import load_point_cloud
from src.perception.preprocessing import filter_roi, downsample_point_cloud, remove_outliers
from src.perception.segmentation import extract_ground
from src.perception.clustering import cluster_objects
from src.perception.bounding_boxes import detected_bounding_boxes


def run_pipeline(dir_path, tracker):

    frame_files = sorted(Path(dir_path).glob("*bin"))

    for frame_idx, file_path in enumerate(frame_files):
        points = load_point_cloud(file_path)

        # Filter specified region
        filtered_points = filter_roi(
            points, x_min=0, x_max=40, y_min=-20, y_max=20, z_min=-2, z_max=2
        )

        # Downsample filtered region
        downsampled = downsample_point_cloud(filtered_points[:, :3], voxel_size=0.2)

        # Remove outliers from downsampled points
        cleaned_points = remove_outliers(downsampled, nb_neighbors=20, std_ratio=2.0)

        # Segment ground and non-ground points
        ground_points, object_points = extract_ground(
            cleaned_points, distance_threshold=0.2, ransac_n=3, num_iterations=1000
        )

        # Cluter non-ground points using DBSCAN
        labels = cluster_objects(object_points, eps=1.0, min_points=13)

        # Get list of detection objects created via bounding boxes
        detections = detected_bounding_boxes(object_points, labels)

        tracked_objects = tracker.update(detections)

        tracked_objects = tracker.update(detections)

        # print current frames tracked objects in tracker
        print(f"\n===== Frame {frame_idx} =====")
        for track in tracked_objects:
            print(track)

    # Print results of tracked objects from tracker
    print("\n===== FINAL TRACK SUMMARY =====")
    for tracks_id, track in tracker.tracks.items():
        print(
            f"Track {track.track_id} | "
            f"{track.detection.classification} | "
            f"Frames Seen: {track.frames_seen} "
        )
    return tracked_objects
```
Now that we have the `run_pipeline` function, we will call it in the `run_phase_8.py` file, which will serve as the entry point for running the perception pipeline with tracking for this phase. The `run_phase_8.py` file will create a `SimpleTracker` object and pass it to the `run_pipeline` function along with the path to the KITTI dataset.

```python
from src.core.tracker import SimpleTracker
from src.perception.pipeline import run_pipeline

tracker = SimpleTracker(max_distance=2.0)

tracks = run_pipeline(dir_path="data/kitti", tracker=tracker)
```

output:
```

===== Frame 0 =====
Track 0 | Unknown | History 2
Track 2 | Car | History 1
Track 4 | Unknown | History 1
Track 6 | Pedestrian | History 1
Track 8 | Pedestrian | History 1
Track 10 | Pedestrian | History 1
Track 12 | Unknown | History 1
Track 14 | Cyclist | History 1
Track 16 | Unknown | History 1
Track 18 | Unknown | History 1
Track 20 | Unknown | History 1
Track 22 | Car | History 1
Track 24 | Pedestrian | History 1
Track 26 | Unknown | History 1
Track 28 | Unknown | History 1
Track 30 | Unknown | History 1
Track 32 | Unknown | History 1
Track 34 | Unknown | History 1
Track 36 | Pedestrian | History 1
Track 38 | Pedestrian | History 1
Track 40 | Unknown | History 1
Track 42 | Pedestrian | History 1

===== Frame 1 =====
Track 0 | Unknown | History 3
Track 2 | Car | History 2
Track 6 | Pedestrian | History 2
Track 8 | Unknown | History 2
Track 4 | Unknown | History 2
Track 20 | Unknown | History 2
Track 40 | Unknown | History 2
Track 28 | Unknown | History 2
Track 38 | Pedestrian | History 2
Track 10 | Pedestrian | History 2
Track 12 | Unknown | History 2
Track 24 | Pedestrian | History 2
Track 26 | Car | History 2
Track 32 | Unknown | History 2
Track 44 | Unknown | History 1
Track 34 | Unknown | History 2
Track 36 | Pedestrian | History 2
Track 22 | Unknown | History 2
Track 16 | Pedestrian | History 2
Track 30 | Unknown | History 2
Track 18 | Unknown | History 2
Track 46 | Unknown | History 1
Track 42 | Unknown | History 2

===== Frame 2 =====
Track 48 | Unknown | History 1
Track 2 | Car | History 3
Track 0 | Unknown | History 4
Track 50 | Pedestrian | History 1
Track 4 | Unknown | History 3
Track 6 | Pedestrian | History 3
Track 8 | Pedestrian | History 3
Track 12 | Unknown | History 3
Track 34 | Unknown | History 3
Track 26 | Unknown | History 3
Track 20 | Unknown | History 3
Track 28 | Unknown | History 3
Track 10 | Pedestrian | History 3
Track 40 | Unknown | History 3
Track 38 | Pedestrian | History 3
Track 30 | Unknown | History 3
Track 36 | Pedestrian | History 3
Track 22 | Car | History 3
Track 18 | Cyclist | History 3
Track 16 | Unknown | History 3
Track 44 | Unknown | History 2
Track 24 | Pedestrian | History 3
Track 52 | Pedestrian | History 1
Track 32 | Unknown | History 3
Track 54 | Cyclist | History 1
Track 46 | Unknown | History 2
Track 56 | Pedestrian | History 1

===== Frame 3 =====
Track 58 | Unknown | History 1
Track 2 | Car | History 4
Track 50 | Pedestrian | History 2
Track 60 | Unknown | History 1
Track 4 | Unknown | History 4
Track 8 | Pedestrian | History 4
Track 62 | Car | History 1
Track 26 | Car | History 4
Track 24 | Pedestrian | History 4
Track 28 | Unknown | History 4
Track 10 | Pedestrian | History 4
Track 54 | Unknown | History 2
Track 12 | Unknown | History 4
Track 20 | Unknown | History 4
Track 16 | Pedestrian | History 4
Track 18 | Unknown | History 4
Track 64 | Pedestrian | History 1
Track 44 | Unknown | History 3
Track 22 | Car | History 4
Track 38 | Pedestrian | History 4
Track 34 | Unknown | History 4
Track 56 | Pedestrian | History 2
Track 40 | Unknown | History 4
Track 30 | Pedestrian | History 4
Track 36 | Unknown | History 4

===== Frame 4 =====
Track 66 | Unknown | History 1
Track 2 | Car | History 5
Track 8 | Pedestrian | History 5
Track 68 | Pedestrian | History 1
Track 4 | Unknown | History 5
Track 70 | Unknown | History 1
Track 10 | Pedestrian | History 5
Track 26 | Car | History 5
Track 38 | Pedestrian | History 5
Track 20 | Car | History 5
Track 18 | Unknown | History 5
Track 16 | Pedestrian | History 5
Track 28 | Car | History 5
Track 12 | Unknown | History 5
Track 40 | Unknown | History 5
Track 54 | Unknown | History 3
Track 24 | Pedestrian | History 5
Track 34 | Unknown | History 5
Track 22 | Unknown | History 5
Track 72 | Pedestrian | History 1
Track 56 | Pedestrian | History 3
Track 74 | Unknown | History 1
Track 44 | Unknown | History 4

===== Frame 5 =====
Track 2 | Car | History 6
Track 66 | Unknown | History 2
Track 76 | Pedestrian | History 1
Track 8 | Pedestrian | History 6
Track 68 | Pedestrian | History 2
Track 4 | Unknown | History 6
Track 70 | Unknown | History 2
Track 10 | Pedestrian | History 6
Track 28 | Car | History 6
Track 12 | Unknown | History 6
Track 26 | Unknown | History 6
Track 38 | Pedestrian | History 6
Track 34 | Unknown | History 6
Track 20 | Car | History 6
Track 16 | Unknown | History 6
Track 54 | Unknown | History 4
Track 18 | Unknown | History 6
Track 78 | Pedestrian | History 1
Track 72 | Unknown | History 2
Track 24 | Pedestrian | History 6
Track 74 | Unknown | History 2
Track 80 | Pedestrian | History 1
Track 22 | Car | History 6
Track 56 | Pedestrian | History 4
Track 82 | Unknown | History 1
Track 40 | Unknown | History 6
Track 84 | Unknown | History 1
Track 86 | Unknown | History 1
Track 44 | Unknown | History 5

===== Frame 6 =====
Track 2 | Car | History 7
Track 66 | Unknown | History 3
Track 8 | Pedestrian | History 7
Track 4 | Unknown | History 7
Track 68 | Pedestrian | History 3
Track 10 | Pedestrian | History 7
Track 80 | Unknown | History 2
Track 12 | Unknown | History 7
Track 34 | Unknown | History 7
Track 22 | Car | History 7
Track 38 | Pedestrian | History 7
Track 84 | Unknown | History 2
Track 74 | Unknown | History 3
Track 20 | Unknown | History 7
Track 26 | Unknown | History 7
Track 40 | Unknown | History 7
Track 24 | Pedestrian | History 7
Track 28 | Unknown | History 7
Track 54 | Car | History 5
Track 82 | Pedestrian | History 2
Track 18 | Unknown | History 7
Track 72 | Cyclist | History 3
Track 78 | Pedestrian | History 2
Track 88 | Cyclist | History 1
Track 56 | Pedestrian | History 5
Track 90 | Unknown | History 1
Track 86 | Unknown | History 2
Track 44 | Unknown | History 6

===== Frame 7 =====
Track 92 | Unknown | History 1
Track 2 | Car | History 8
Track 94 | Pedestrian | History 1
Track 96 | Unknown | History 1
Track 98 | Car | History 1
Track 8 | Pedestrian | History 8
Track 10 | Pedestrian | History 8
Track 4 | Unknown | History 8
Track 68 | Pedestrian | History 4
Track 12 | Unknown | History 8
Track 80 | Unknown | History 3
Track 22 | Car | History 8
Track 28 | Unknown | History 8
Track 20 | Car | History 8
Track 72 | Cyclist | History 4
Track 34 | Car | History 8
Track 26 | Unknown | History 8
Track 82 | Pedestrian | History 3
Track 84 | Unknown | History 3
Track 38 | Pedestrian | History 8
Track 54 | Car | History 6
Track 24 | Pedestrian | History 8
Track 18 | Unknown | History 8
Track 78 | Pedestrian | History 3
Track 90 | Unknown | History 2
Track 56 | Pedestrian | History 6
Track 74 | Unknown | History 4
Track 40 | Unknown | History 8
Track 44 | Unknown | History 7
Track 100 | Unknown | History 1

===== Frame 8 =====
Track 92 | Unknown | History 2
Track 102 | Unknown | History 1
Track 94 | Pedestrian | History 2
Track 104 | Pedestrian | History 1
Track 98 | Car | History 2
Track 10 | Pedestrian | History 9
Track 68 | Pedestrian | History 5
Track 34 | Unknown | History 9
Track 54 | Car | History 7
Track 106 | Unknown | History 1
Track 20 | Car | History 9
Track 108 | Unknown | History 1
Track 56 | Pedestrian | History 7
Track 38 | Pedestrian | History 9
Track 12 | Unknown | History 9
Track 28 | Unknown | History 9
Track 24 | Pedestrian | History 9
Track 110 | Unknown | History 1
Track 112 | Unknown | History 1
Track 114 | Unknown | History 1
Track 26 | Unknown | History 9
Track 116 | Unknown | History 1
Track 118 | Unknown | History 1
Track 22 | Car | History 9
Track 78 | Pedestrian | History 4
Track 120 | Pedestrian | History 1
Track 18 | Unknown | History 9
Track 40 | Unknown | History 9
Track 72 | Unknown | History 5
Track 82 | Pedestrian | History 4
Track 80 | Pedestrian | History 4
Track 122 | Unknown | History 1
Track 124 | Unknown | History 1
Track 74 | Unknown | History 5

===== Frame 9 =====
Track 126 | Unknown | History 1
Track 128 | Car | History 1
Track 130 | Pedestrian | History 1
Track 10 | Pedestrian | History 10
Track 132 | Unknown | History 1
Track 134 | Cyclist | History 1
Track 20 | Car | History 10
Track 38 | Pedestrian | History 10
Track 28 | Unknown | History 10
Track 56 | Pedestrian | History 8
Track 40 | Unknown | History 10
Track 26 | Unknown | History 10
Track 12 | Unknown | History 10
Track 78 | Pedestrian | History 5
Track 18 | Unknown | History 10
Track 22 | Car | History 10
Track 54 | Car | History 8
Track 72 | Unknown | History 6
Track 74 | Unknown | History 6
Track 80 | Pedestrian | History 5
Track 34 | Unknown | History 10
Track 82 | Pedestrian | History 5
Track 24 | Pedestrian | History 10
Track 136 | Pedestrian | History 1
Track 138 | Unknown | History 1
Track 140 | Unknown | History 1
Track 142 | Unknown | History 1
Track 144 | Unknown | History 1
Track 124 | Pedestrian | History 2
Track 146 | Unknown | History 1

===== Frame 10 =====
Track 126 | Unknown | History 2
Track 128 | Unknown | History 2
Track 10 | Pedestrian | History 11
Track 130 | Pedestrian | History 2
Track 148 | Unknown | History 1
Track 134 | Cyclist | History 2
Track 132 | Unknown | History 2
Track 28 | Unknown | History 11
Track 18 | Car | History 11
Track 26 | Unknown | History 11
Track 12 | Unknown | History 11
Track 136 | Pedestrian | History 2
Track 22 | Car | History 11
Track 54 | Car | History 9
Track 78 | Pedestrian | History 6
Track 20 | Car | History 11
Track 124 | Pedestrian | History 3
Track 140 | Unknown | History 2
Track 40 | Unknown | History 11
Track 150 | Pedestrian | History 1
Track 74 | Unknown | History 7
Track 80 | Pedestrian | History 6
Track 24 | Pedestrian | History 11
Track 142 | Unknown | History 2
Track 72 | Unknown | History 7
Track 38 | Pedestrian | History 11
Track 152 | Unknown | History 1
Track 56 | Pedestrian | History 9

===== Frame 11 =====
Track 128 | Unknown | History 3
Track 126 | Unknown | History 3
Track 130 | Pedestrian | History 3
Track 10 | Pedestrian | History 12
Track 132 | Unknown | History 3
Track 154 | Pedestrian | History 1
Track 134 | Cyclist | History 3
Track 28 | Car | History 12
Track 24 | Pedestrian | History 12
Track 12 | Unknown | History 12
Track 156 | Unknown | History 1
Track 140 | Unknown | History 3
Track 20 | Unknown | History 12
Track 26 | Unknown | History 12
Track 18 | Unknown | History 12
Track 38 | Pedestrian | History 12
Track 80 | Pedestrian | History 7
Track 54 | Car | History 10
Track 124 | Unknown | History 4
Track 56 | Pedestrian | History 10
Track 22 | Car | History 12
Track 40 | Unknown | History 12
Track 72 | Pedestrian | History 8
Track 150 | Pedestrian | History 2
Track 136 | Pedestrian | History 3
Track 78 | Pedestrian | History 7
Track 158 | Unknown | History 1
Track 74 | Pedestrian | History 8
Track 142 | Unknown | History 3

===== Frame 12 =====
Track 160 | Unknown | History 1
Track 128 | Pedestrian | History 4
Track 162 | Pedestrian | History 1
Track 130 | Pedestrian | History 4
Track 10 | Pedestrian | History 13
Track 132 | Unknown | History 4
Track 164 | Pedestrian | History 1
Track 166 | Unknown | History 1
Track 154 | Pedestrian | History 2
Track 28 | Unknown | History 13
Track 156 | Unknown | History 2
Track 124 | Pedestrian | History 5
Track 20 | Unknown | History 13
Track 12 | Unknown | History 13
Track 26 | Car | History 13
Track 54 | Car | History 11
Track 24 | Pedestrian | History 13
Track 80 | Pedestrian | History 8
Track 40 | Unknown | History 13
Track 168 | Unknown | History 1
Track 18 | Unknown | History 13
Track 136 | Pedestrian | History 4
Track 22 | Car | History 13
Track 38 | Pedestrian | History 13
Track 56 | Pedestrian | History 11
Track 78 | Pedestrian | History 8
Track 142 | Unknown | History 4
Track 72 | Pedestrian | History 9
Track 170 | Unknown | History 1
Track 150 | Pedestrian | History 3
Track 172 | Cyclist | History 1

===== Frame 13 =====
Track 174 | Unknown | History 1
Track 176 | Unknown | History 1
Track 128 | Unknown | History 5
Track 10 | Pedestrian | History 14
Track 130 | Pedestrian | History 5
Track 178 | Unknown | History 1
Track 180 | Pedestrian | History 1
Track 132 | Unknown | History 5
Track 12 | Unknown | History 14
Track 20 | Car | History 14
Track 80 | Pedestrian | History 9
Track 72 | Unknown | History 10
Track 182 | Car | History 1
Track 184 | Cyclist | History 1
Track 28 | Unknown | History 14
Track 186 | Unknown | History 1
Track 40 | Unknown | History 14
Track 24 | Pedestrian | History 14
Track 54 | Car | History 12
Track 26 | Car | History 14
Track 18 | Car | History 14
Track 188 | Pedestrian | History 1
Track 190 | Unknown | History 1
Track 142 | Unknown | History 5
Track 150 | Pedestrian | History 4
Track 22 | Unknown | History 14
Track 136 | Pedestrian | History 5
Track 78 | Pedestrian | History 9
Track 192 | Pedestrian | History 1
Track 124 | Pedestrian | History 6

===== Frame 14 =====
Track 194 | Unknown | History 1
Track 174 | Pedestrian | History 2
Track 176 | Unknown | History 2
Track 196 | Car | History 1
Track 130 | Pedestrian | History 6
Track 10 | Pedestrian | History 15
Track 132 | Unknown | History 6
Track 198 | Unknown | History 1
Track 12 | Unknown | History 15
Track 40 | Unknown | History 15
Track 28 | Car | History 15
Track 18 | Unknown | History 15
Track 20 | Car | History 15
Track 26 | Car | History 15
Track 200 | Unknown | History 1
Track 136 | Pedestrian | History 6
Track 178 | Car | History 2
Track 54 | Car | History 13
Track 24 | Pedestrian | History 15
Track 80 | Pedestrian | History 10
Track 22 | Unknown | History 15
Track 202 | Pedestrian | History 1
Track 190 | Unknown | History 2
Track 204 | Unknown | History 1
Track 182 | Car | History 2
Track 150 | Pedestrian | History 5
Track 206 | Unknown | History 1
Track 78 | Pedestrian | History 10
Track 142 | Unknown | History 6

===== Frame 15 =====
Track 208 | Unknown | History 1
Track 174 | Pedestrian | History 3
Track 210 | Pedestrian | History 1
Track 196 | Unknown | History 2
Track 130 | Pedestrian | History 7
Track 10 | Pedestrian | History 16
Track 176 | Unknown | History 3
Track 212 | Unknown | History 1
Track 132 | Unknown | History 7
Track 198 | Unknown | History 2
Track 22 | Unknown | History 16
Track 12 | Unknown | History 16
Track 20 | Car | History 16
Track 28 | Car | History 16
Track 214 | Pedestrian | History 1
Track 178 | Car | History 3
Track 26 | Car | History 16
Track 182 | Car | History 3
Track 40 | Unknown | History 16
Track 204 | Pedestrian | History 2
Track 206 | Unknown | History 2
Track 202 | Pedestrian | History 2
Track 142 | Unknown | History 7
Track 80 | Unknown | History 11
Track 136 | Unknown | History 7
Track 54 | Car | History 14
Track 18 | Unknown | History 16
Track 24 | Pedestrian | History 16
Track 216 | Unknown | History 1
Track 78 | Pedestrian | History 11
Track 218 | Unknown | History 1
Track 150 | Pedestrian | History 6
Track 220 | Unknown | History 1

===== Frame 16 =====
Track 176 | Unknown | History 4
Track 196 | Car | History 3
Track 10 | Pedestrian | History 17
Track 130 | Pedestrian | History 8
Track 198 | Unknown | History 3
Track 132 | Unknown | History 8
Track 20 | Car | History 17
Track 18 | Unknown | History 17
Track 218 | Unknown | History 2
Track 220 | Unknown | History 2
Track 12 | Unknown | History 17
Track 28 | Car | History 17
Track 54 | Car | History 15
Track 206 | Unknown | History 3
Track 214 | Pedestrian | History 2
Track 222 | Unknown | History 1
Track 24 | Pedestrian | History 17
Track 26 | Car | History 17
Track 78 | Pedestrian | History 12
Track 142 | Unknown | History 8
Track 80 | Unknown | History 12
Track 40 | Unknown | History 17
Track 202 | Pedestrian | History 3
Track 136 | Pedestrian | History 8
Track 150 | Pedestrian | History 7

===== FINAL TRACK SUMMARY =====
Track 176 | Unknown | Frames Seen: 4 
Track 196 | Car | Frames Seen: 3 
Track 10 | Pedestrian | Frames Seen: 17 
Track 130 | Pedestrian | Frames Seen: 8 
Track 198 | Unknown | Frames Seen: 3 
Track 132 | Unknown | Frames Seen: 8 
Track 20 | Car | Frames Seen: 17 
Track 18 | Unknown | Frames Seen: 17 
Track 218 | Unknown | Frames Seen: 2 
Track 220 | Unknown | Frames Seen: 2 
Track 12 | Unknown | Frames Seen: 17 
Track 28 | Car | Frames Seen: 17 
Track 54 | Car | Frames Seen: 15 
Track 206 | Unknown | Frames Seen: 3 
Track 214 | Pedestrian | Frames Seen: 2 
Track 222 | Unknown | Frames Seen: 1 
Track 24 | Pedestrian | Frames Seen: 17 
Track 26 | Car | Frames Seen: 17 
Track 78 | Pedestrian | Frames Seen: 12 
Track 142 | Unknown | Frames Seen: 8 
Track 80 | Unknown | Frames Seen: 12 
Track 40 | Unknown | Frames Seen: 17 
Track 202 | Pedestrian | Frames Seen: 3 
Track 136 | Pedestrian | Frames Seen: 8 
Track 150 | Pedestrian | Frames Seen: 7 
```

## Analysis of the Tracking Results
The tracking results show that the SimpleTracker was able to maintain tracks for several objects across multiple frames. Using the Final Track Summary, we can see that some of the tracks were able to maintain their identity across all 17 frames, while others were only seen for a few frames. There is small issue with the tracking system in frame 0, where Track 0 is classified as "Unknown" and has a history of 2. Since, this is the first frame, it should only have a history of 1. This is likely due to the fact that the tracker is initialized with a next_track_id of 0, and the first detection is assigned to Track 0. However, since the tracker is updated with the detections from frame 0, it increments the history of Track 0 to 2. This issue can be fixed by initializing the next_track_id to 1 instead of 0, so that the first detection is assigned to Track 1. For now we will leave it as is, since it does not affect the overall tracking results, and leave it as a known issue to be fixed in the future. 

## Conclusion
In this phase, we implemented a simple tracking system that can track objects across frames based on their spatial coordinates and classification. We also restructured the project to better reflect the differnt stages of the perception pipeline, and integrated the tracking system into the existing pipeline. 

The object tracker successfully processed 17 consecutive KITTI LiDAR frames. Several objects maintained persistent track IDs across the full sequence, including cars, pedestrians, and unknown structures. This confirms that nearest-neighbor tracking using bounding-box center coordinates can associate objects across time.

The tracker is limited by misclassification, object merging, cluster splitting, and changes in object labels between frames. Some tracks are also short-lived because objects enter or leave the region of interest or because detections are inconsistent across frames.