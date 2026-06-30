# Phase 9 - Velocity Estimation
In this phase, the goal is to use each track's center history to estimate motion. Using the center history `track.history`, which contains the center coordinates of the object in each frame, we can calculate the velocity of the object by computing the difference in position over time. We can compute the velocity from the displacement over time using the formula:
$$
v = \frac{\Delta d}{\Delta t}
$$
where $\Delta d$ is the change in position (displacement) and $\Delta t$ is the change in time (time interval). 

## KITTI Dataset Frame Rate
The KITTI dataset provides LiDAR frames at a frame rate of 10 Hz, which means that the time interval between consecutive frames is 0.1 seconds. Therefore, when calculating the velocity, we can use $\Delta t = 0.1$ seconds.

## Procedures for Velocity Estimation
1. Add a method to the `Track` class that calculates the velocity based on the center history. This method will compute the difference in position between the last two frames and divide it by the time interval (0.1 seconds) to calcualte its instataneous velocity.
2. Add a method to the `Track` class that calculates the average velocity over the entire history of the track. This method will compute the total displacement from the first to the last frame and divide it by the total time elapsed (number of recorded center history * 0.1 seconds).
3. In the `run_phase_9.py` file, after running the tracking pipeline, iterate through the tracks and call the velocity estimation methods to compute and print the velocity for each track.
4. Visualize the frames with bounding boxes.
5. Run the `run_phase_9.py` script to see the velocity estimation results for each tracked object in the KITTI dataset.
6. Optional: The velocity Convert the velocity from meters per second to miles per hour (mph) by creating a new method in the `Track` class that converts the velocity from m/s to mph using the conversion factor: 1 m/s = 2.23694 mph. This method can be called after computing the velocity to display the speed in mph.

### Step 1: Implement Velocity Calculation in Track Class
```python
    def compute_velocity(
            self, 
            dt=0.1
    ):
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

        # Calculate velocity as displacement over time
        velocity = displacement / dt
        
        return velocity
```

### Step 2: Implement Average Velocity Calculation in Track Class
```python
    def compute_average_velocity(
            self, 
            dt=0.1
    ):
        if len(self.history) < 2:
            return 0.0
        
        # Retrieve the first and last center positions from the history
        first_center = self.history[0]
        last_center = self.history[-1]

        # Using only x and y from each of the center calculate total displacement
        total_displacement = np.linalg.norm(
            last_center[:2] - first_center[:2]
        )

        # Calculate total time elapsed based on number of frames
        total_time = (len(self.history) - 1) * dt

        # Calculate average velocity as total displacement over total time
        average_velocity = total_displacement / total_time
        
        return average_velocity
```

### Step 3: Update run_phase_9.py to Compute and Print Velocities
```python
# After running the tracking pipeline
for track in tracker.tracks.values():
    velocity = track.compute_velocity()
    average_velocity = track.compute_average_velocity()
    print(
        f"Track {track.track_id} | "
        f"{track.detection.classification} | "
        f"Speed={speed:.2f} m/s | "
        f"Avg Speed={avg_speed:.2f} m/s | "
        f"History={len(track.history)}"       
    )
```


### Step 4: Visualize frames with Bounding Boxes
To visualize the frames with bounding boxes, we create a function in the `open3d_viewer.py` file that takes a dictionary called `frames` as input. This dictionary contains the point cloud data of each frame after they have been processed by the pipeline, and the Open3D bounding box objects for each detected object in a frame. 

```python
def animate_frames_with_boxes(frames, delay=0.2):
    # Create an Open3D visualizer window
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="Tracked KITTI Sequence")

    # Add the first frame's point cloud and bounding boxes to the visualizer
    pcd = frames[0]["pcd"]
    boxes = frames[0]["boxes"]

    # Add the point cloud and bounding boxes to the visualizer
    vis.add_geometry(pcd)

    # Add the bounding boxes to the visualizer
    for box in boxes:
        vis.add_geometry(box)

    # Keep track of the current boxes to remove them in the next frame
    current_boxes = boxes
    
    # Loop through the frames and update the visualizer
    for frame_idx, frame in enumerate(frames):
        # Remove old boxes
        for box in current_boxes:
            vis.remove_geometry(box, reset_bounding_box=False)

        # Update point cloud
        pcd.points = frame["pcd"].points
        vis.update_geometry(pcd)

        # Add new boxes
        current_boxes = frame["boxes"]

        # Add the new bounding boxes to the visualizer
        for box in current_boxes:
            vis.add_geometry(box, reset_bounding_box=False)

        # Update the visualizer
        vis.poll_events()
        vis.update_renderer()

        print(f"Showing fame {frame_idx}")

        # Delay to control the speed of the animation
        time.sleep(delay)

    # Destroy the visualizer window after the animation is complete
    vis.destroy_window()
```

### Step 5: Run the run_phase_9.py Script
This script will run the tracking pipeline on the KITTI dataset, compute the velocities for each tracked object, and it will visualize each of the frames along with the bounding boxes for the detected objects. The output will display the track ID, classification, speed, average speed, and history length for each tracked object.

```python
import open3d as o3d
from src.core.tracking import SimpleTracker
from src.perception.pipeline import run_pipeline
from src.visualization.open3d_viewer import animate_frames_with_boxes
from pathlib import Path

tracker = SimpleTracker()

frame_files = sorted(
    Path("datasets/kitti").glob("*bin")
)

frames = []

for frame_idx, file_path in enumerate(frame_files):
    object_points, detections = run_pipeline(str(file_path))
    tracked_objects = tracker.update(detections)

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(object_points[:, :3])

    boxes = []

    for detection in detections:
        bbox = detection.bbox
        bbox.color = [1, 0, 0]
        boxes.append(bbox)   

    frames.append({
        "pcd": pcd,
        "boxes": boxes
    })

    for track in tracked_objects:
        speed = track.compute_velocity(dt=0.1)
        avg_speed = track.compute_average_velocity(dt=0.1)

        if len(track.history) > 9:
                
            print(
                f"Track {track.track_id} | "
                f"{track.detection.classification} | "
                f"Speed={speed:.2f} m/s | "
                f"Avg Speed={avg_speed:.2f} m/s | "
                f"History={len(track.history)}"       
            )

    
animate_frames_with_boxes(frames, delay=0.3)
```
__Note:__ The `pipeline.py` file was reconfigured to return both the object points and the detections one single frame at a time. This is to ensure that we can visualize the bounding boxes for each frame along with the point cloud data. 

To analyze the output, you can see that the script prints the track ID, classification (e.g., Car, Pedestrian, Unknown), current speed, average speed, and the length of the history for each tracked object. However, we only print the tracks that have a history of length greater than 9. This is to ensure that we have enough data points to compute a meaningful average speed. The output will look something like this:


```Text
Output:
Track 12 | Pedestrian | Speed=6.69 m/s | Avg Speed=6.71 m/s | History=10
Track 24 | Car | Speed=5.26 m/s | Avg Speed=4.89 m/s | History=10
Track 46 | Pedestrian | Speed=6.40 m/s | Avg Speed=4.73 m/s | History=10
Track 32 | Unknown | Speed=3.23 m/s | Avg Speed=4.80 m/s | History=10
Track 50 | Unknown | Speed=3.69 m/s | Avg Speed=4.76 m/s | History=10
Track 30 | Unknown | Speed=4.90 m/s | Avg Speed=5.26 m/s | History=10
Track 16 | Unknown | Speed=8.70 m/s | Avg Speed=5.17 m/s | History=10
Track 28 | Pedestrian | Speed=3.89 m/s | Avg Speed=4.81 m/s | History=10
Track 22 | Unknown | Speed=4.36 m/s | Avg Speed=5.42 m/s | History=10
Track 26 | Car | Speed=7.13 m/s | Avg Speed=5.13 m/s | History=10
Track 42 | Unknown | Speed=19.81 m/s | Avg Speed=6.38 m/s | History=10
Track 12 | Pedestrian | Speed=6.71 m/s | Avg Speed=6.70 m/s | History=11
Track 32 | Unknown | Speed=6.80 m/s | Avg Speed=4.98 m/s | History=11
Track 22 | Car | Speed=5.99 m/s | Avg Speed=5.48 m/s | History=11
Track 42 | Unknown | Speed=7.75 m/s | Avg Speed=6.52 m/s | History=11
Track 30 | Unknown | Speed=4.92 m/s | Avg Speed=5.21 m/s | History=11
Track 16 | Unknown | Speed=3.64 m/s | Avg Speed=5.01 m/s | History=11
Track 26 | Car | Speed=1.60 m/s | Avg Speed=4.49 m/s | History=11
Track 24 | Car | Speed=4.87 m/s | Avg Speed=4.89 m/s | History=11
Track 50 | Unknown | Speed=5.67 m/s | Avg Speed=4.85 m/s | History=11
Track 28 | Pedestrian | Speed=4.66 m/s | Avg Speed=4.80 m/s | History=11
Track 46 | Pedestrian | Speed=4.16 m/s | Avg Speed=4.67 m/s | History=11
Track 70 | Unknown | Speed=5.12 m/s | Avg Speed=4.82 m/s | History=10
Track 74 | Pedestrian | Speed=5.27 m/s | Avg Speed=5.06 m/s | History=10
Track 12 | Pedestrian | Speed=7.34 m/s | Avg Speed=6.76 m/s | History=12
Track 32 | Car | Speed=4.90 m/s | Avg Speed=4.97 m/s | History=12
Track 28 | Pedestrian | Speed=4.80 m/s | Avg Speed=4.79 m/s | History=12
Track 16 | Unknown | Speed=6.20 m/s | Avg Speed=5.11 m/s | History=12
Track 42 | Car | Speed=12.73 m/s | Avg Speed=4.94 m/s | History=12
Track 24 | Unknown | Speed=5.99 m/s | Avg Speed=4.98 m/s | History=12
Track 30 | Unknown | Speed=4.91 m/s | Avg Speed=5.18 m/s | History=12
Track 46 | Pedestrian | Speed=6.39 m/s | Avg Speed=4.83 m/s | History=12
Track 22 | Unknown | Speed=0.25 m/s | Avg Speed=5.00 m/s | History=12
Track 78 | Car | Speed=6.67 m/s | Avg Speed=3.96 m/s | History=10
Track 82 | Pedestrian | Speed=4.25 m/s | Avg Speed=4.82 m/s | History=10
Track 26 | Car | Speed=4.56 m/s | Avg Speed=4.32 m/s | History=12
Track 50 | Unknown | Speed=6.50 m/s | Avg Speed=5.00 m/s | History=12
Track 70 | Pedestrian | Speed=2.68 m/s | Avg Speed=4.60 m/s | History=11
Track 74 | Pedestrian | Speed=4.48 m/s | Avg Speed=5.00 m/s | History=11
Track 12 | Pedestrian | Speed=6.44 m/s | Avg Speed=6.73 m/s | History=13
Track 32 | Unknown | Speed=5.34 m/s | Avg Speed=4.99 m/s | History=13
Track 42 | Unknown | Speed=10.45 m/s | Avg Speed=5.39 m/s | History=13
Track 24 | Unknown | Speed=5.18 m/s | Avg Speed=4.99 m/s | History=13
Track 16 | Unknown | Speed=1.82 m/s | Avg Speed=4.81 m/s | History=13
Track 30 | Car | Speed=9.38 m/s | Avg Speed=5.53 m/s | History=13
Track 78 | Car | Speed=6.05 m/s | Avg Speed=4.15 m/s | History=11
Track 28 | Pedestrian | Speed=4.84 m/s | Avg Speed=4.80 m/s | History=13
Track 50 | Unknown | Speed=3.95 m/s | Avg Speed=4.91 m/s | History=13
Track 22 | Unknown | Speed=3.51 m/s | Avg Speed=4.87 m/s | History=13
Track 26 | Car | Speed=5.84 m/s | Avg Speed=4.42 m/s | History=13
Track 46 | Pedestrian | Speed=1.67 m/s | Avg Speed=4.54 m/s | History=13
Track 82 | Pedestrian | Speed=5.01 m/s | Avg Speed=4.84 m/s | History=11
Track 70 | Unknown | Speed=5.71 m/s | Avg Speed=4.29 m/s | History=12
Track 12 | Pedestrian | Speed=6.04 m/s | Avg Speed=6.68 m/s | History=14
Track 74 | Pedestrian | Speed=5.84 m/s | Avg Speed=5.07 m/s | History=12
Track 16 | Unknown | Speed=6.43 m/s | Avg Speed=4.94 m/s | History=14
Track 24 | Unknown | Speed=5.09 m/s | Avg Speed=5.00 m/s | History=14
Track 42 | Unknown | Speed=1.26 m/s | Avg Speed=5.07 m/s | History=14
Track 32 | Unknown | Speed=5.27 m/s | Avg Speed=5.01 m/s | History=14
Track 50 | Unknown | Speed=5.65 m/s | Avg Speed=4.96 m/s | History=14
Track 78 | Car | Speed=8.30 m/s | Avg Speed=4.27 m/s | History=12
Track 30 | Car | Speed=7.49 m/s | Avg Speed=5.63 m/s | History=14
Track 28 | Pedestrian | Speed=5.21 m/s | Avg Speed=4.83 m/s | History=14
Track 22 | Unknown | Speed=5.73 m/s | Avg Speed=4.94 m/s | History=14
Track 90 | Pedestrian | Speed=5.85 m/s | Avg Speed=4.91 m/s | History=10
Track 26 | Unknown | Speed=9.30 m/s | Avg Speed=4.74 m/s | History=14
Track 74 | Pedestrian | Speed=5.81 m/s | Avg Speed=4.88 m/s | History=13
Track 12 | Pedestrian | Speed=6.23 m/s | Avg Speed=6.65 m/s | History=15
Track 96 | Unknown | Speed=5.20 m/s | Avg Speed=4.65 m/s | History=10
Track 16 | Unknown | Speed=4.20 m/s | Avg Speed=4.88 m/s | History=15
Track 50 | Unknown | Speed=5.76 m/s | Avg Speed=5.02 m/s | History=15
Track 32 | Car | Speed=4.63 m/s | Avg Speed=4.98 m/s | History=15
Track 22 | Unknown | Speed=3.85 m/s | Avg Speed=4.86 m/s | History=15
Track 24 | Car | Speed=8.37 m/s | Avg Speed=5.24 m/s | History=15
Track 30 | Car | Speed=5.05 m/s | Avg Speed=5.57 m/s | History=15
Track 42 | Unknown | Speed=9.15 m/s | Avg Speed=5.02 m/s | History=15
Track 28 | Pedestrian | Speed=6.45 m/s | Avg Speed=4.94 m/s | History=15
Track 78 | Car | Speed=4.18 m/s | Avg Speed=4.18 m/s | History=13
Track 94 | Pedestrian | Speed=3.67 m/s | Avg Speed=4.54 m/s | History=10
Track 26 | Unknown | Speed=6.62 m/s | Avg Speed=3.96 m/s | History=15
Track 12 | Pedestrian | Speed=6.00 m/s | Avg Speed=6.60 m/s | History=16
Track 74 | Pedestrian | Speed=7.96 m/s | Avg Speed=5.00 m/s | History=14
Track 26 | Unknown | Speed=12.94 m/s | Avg Speed=4.13 m/s | History=16
Track 16 | Unknown | Speed=4.89 m/s | Avg Speed=4.88 m/s | History=16
Track 24 | Car | Speed=7.52 m/s | Avg Speed=5.39 m/s | History=16
Track 32 | Car | Speed=4.40 m/s | Avg Speed=4.91 m/s | History=16
Track 22 | Unknown | Speed=4.51 m/s | Avg Speed=4.84 m/s | History=16
Track 30 | Car | Speed=5.64 m/s | Avg Speed=5.55 m/s | History=16
Track 50 | Unknown | Speed=3.89 m/s | Avg Speed=4.94 m/s | History=16
Track 94 | Unknown | Speed=1.45 m/s | Avg Speed=4.17 m/s | History=11
Track 78 | Car | Speed=5.66 m/s | Avg Speed=4.27 m/s | History=14
Track 28 | Pedestrian | Speed=3.18 m/s | Avg Speed=4.80 m/s | History=16
Track 12 | Pedestrian | Speed=8.11 m/s | Avg Speed=6.69 m/s | History=17
Track 74 | Pedestrian | Speed=5.47 m/s | Avg Speed=5.02 m/s | History=15
Track 24 | Car | Speed=4.21 m/s | Avg Speed=5.31 m/s | History=17
Track 22 | Unknown | Speed=6.77 m/s | Avg Speed=4.89 m/s | History=17
Track 16 | Unknown | Speed=5.30 m/s | Avg Speed=4.90 m/s | History=17
Track 32 | Car | Speed=8.15 m/s | Avg Speed=5.11 m/s | History=17
Track 78 | Car | Speed=4.81 m/s | Avg Speed=4.17 m/s | History=15
Track 50 | Unknown | Speed=7.60 m/s | Avg Speed=5.08 m/s | History=17
Track 28 | Pedestrian | Speed=5.08 m/s | Avg Speed=4.82 m/s | History=17
Track 30 | Car | Speed=7.27 m/s | Avg Speed=5.63 m/s | History=17
Track 94 | Unknown | Speed=15.56 m/s | Avg Speed=5.18 m/s | History=12

```

To better understand the tracking results, we can analyze the final summary of the tracked objects with tracks that have a value of frames_seen greater than 9. This will give us a better understanding of the performance of the tracking algorithm and the velocity estimation.

```python
# After running the tracking pipeline
for track in list(tracker.tracks.values()):
    if track.frames_seen >= 10:
        print(track)
```

```
Output:
Track 10 | Pedestrian | Speed=7.73 m/s | Avg Speed=6.71 m/s | History 17
Track 20 | Car | Speed=4.21 m/s | Avg Speed=5.31 m/s | History 17
Track 18 | Car | Speed=7.75 m/s | Avg Speed=4.79 m/s | History 17
Track 12 | Unknown | Speed=5.29 m/s | Avg Speed=4.90 m/s | History 17
Track 28 | Car | Speed=8.15 m/s | Avg Speed=5.05 m/s | History 17
Track 52 | Car | Speed=4.81 m/s | Avg Speed=4.17 m/s | History 15
Track 24 | Pedestrian | Speed=4.79 m/s | Avg Speed=4.79 m/s | History 17
Track 26 | Car | Speed=7.27 m/s | Avg Speed=5.63 m/s | History 17
Track 36 | Pedestrian | Speed=3.49 m/s | Avg Speed=3.11 m/s | History 17
Track 90 | Unknown | Speed=15.56 m/s | Avg Speed=5.18 m/s | History 12
Track 40 | Unknown | Speed=6.25 m/s | Avg Speed=5.02 m/s | History 17
```
## Analysis of Results
The questions "Do these results make sense?" and "Are these speeds reasonable?" can be answered by analyzing the output of the velocity estimation. An important thing to consider is that the KITTI dataset was collected from a moving vehicle, which means that the camera is not stationary. This can affect the perceived speed of the objects in the scene, as the motion of the camera can introduce additinal velocity components to the objects being tracked. 

### Analysis by Object Type
__Car__

|Track ID|Instantaneous Speed (m/s) | Average Speed (m/s) | Analysis |
|--------|---------------------------|--------------------|---------|
| 20     | 4.21                      | 5.31               | The instantaneous is slightly lower than the average speed, which may indicate that the car is decelerating. |
| 18     | 7.75                      | 4.79               | The instantaneous speed is significantly higher than the average speed, which may indicate that the car has recently accelerated. |
| 28     | 8.15                      | 5.05               | The instantaneous speed is higher than the average speed, which may indicate that the car has recently accelerated or the instantaneous was likely affected by jitter|
| 52     | 4.81                      | 4.17               | The instantaneous speed is slightly higher than the average speed, which may indicate that the car is accelerating. |
| 26     | 7.27                      | 5.63               | The instantaneous speed is higher than the average speed, which may indicate that the car has recently accelerated. |

The average speeds for the cars are consistent, clustering around 4-5 m/s(11-13 mph), which is reasonable for urban driving conditions. The instantaneous speeds vary more, which is expected due to acceleration and deceleration events. This indicates that the tracking system is stable and can handle the dynamics of moving vehicles.

__Pedestrian__

|Track ID|Instantaneous Speed (m/s) | Average Speed (m/s) | Analysis |
|--------|---------------------------|--------------------|---------|
| 10     | 7.73                      | 6.71               | These speeds are remarkably high for a pedestrian. This suggests that the tracking system may have either misclassified a fast-moving object as a pedestrian or noise in the tracking data affected the velocity estimation. |
| 24     | 4.79                      | 4.79               | The instantaneous and average speeds are equal, which may indicate that the pedestrian is moving at a constant speed. However, this speed is still high for a pedestrian, suggesting potential misclassification or noise in the tracking data. |
| 36     | 3.49                      | 3.11               | These speeds are more reasonable for a pedestrian, indicating that the tracking system is likely functioning correctly for this track. |

Normally, a pedestrian's walking speed is around 1-2 m/s (3-4 mph) and running speed can be around 3-5 m/s (7-11 mph). The high speeds observed in some tracks suggest that there may be misclassifications or noise in the tracking data. Furthermore, the tracking system may have likely inflated the speeds due to motion of the camera mounted on the moving vehicle, which can affect the perceived speed of objects in the scene. Additionally, the tracking system speed estimation may be affected by the center estimation noise and bounding box jitter, which can lead to overestimation of the speed.

__Unknown__

|Track ID|Instantaneous Speed (m/s) | Average Speed (m/s) | Analysis |
|--------|---------------------------|--------------------|---------|
| 12     | 5.29                      | 4.90               | |   
| 40     | 6.25                      | 5.02               | |
| 90     | 15.56                     | 5.18               | The average speed of this object is significantly lesser than the recorded instataneous speed. This may suggest that the instatenous value was affected by a either a noisy update or a change was detected in the cluster itself. |


Although, the average speeds for the unknown objects are reasonable, the instantaneous speeds vary significantly. This may indicate that the tracking system is struggling to maintain a consistent track on these objects, leading to fluctuations in the estimated speed. The high instantaneous speed of track 90 suggests that there may have been a sudden change in the object's motion or a misclassification.

Since, each track contains a history of the center positions, we can enhance the average velocity estimation by computing the average over all frame-to-frame displacements, rather than just the first and last positions. This would provide a more robust estimate of the average speed, especially for tracks with longer histories.

```python
    def compute_average_velocity(
            self, 
            dt=0.1
    ):
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
```

This updated method measures the actual path taken by the object, rather than just the straight-line distance between the first and last points. This should provide a more accurate representation of the object's average speed, especially for objects that may have changed direction or speed during the tracking period.

### Enhancing Average Velocity Estimation Results
After implementing the updated average velocity estimation method, the `run_phase_9.py` script was run to see how the results change. The new average velocity values should be more representative of the object's actual motion, especially for tracks with longer histories or more complex movement patterns.

__Trial 1:__
```text
Output:
Track 10 | Pedestrian | Speed=8.11 m/s | Avg Speed=6.71 m/s | History 17
Track 86 | Unknown | Speed=4.55 m/s | Avg Speed=5.67 m/s | History 13
Track 20 | Car | Speed=4.21 m/s | Avg Speed=7.03 m/s | History 17
Track 18 | Unknown | Speed=6.77 m/s | Avg Speed=5.15 m/s | History 17
Track 12 | Unknown | Speed=5.29 m/s | Avg Speed=5.06 m/s | History 17
Track 28 | Car | Speed=8.12 m/s | Avg Speed=7.39 m/s | History 17
Track 54 | Car | Speed=4.81 m/s | Avg Speed=5.09 m/s | History 15
Track 24 | Pedestrian | Speed=5.08 m/s | Avg Speed=4.83 m/s | History 17
Track 26 | Car | Speed=7.27 m/s | Avg Speed=6.28 m/s | History 17
Track 36 | Pedestrian | Speed=3.65 m/s | Avg Speed=3.17 m/s | History 17
Track 88 | Unknown | Speed=15.56 m/s | Avg Speed=5.44 m/s | History 12
Track 40 | Unknown | Speed=6.25 m/s | Avg Speed=5.05 m/s | History 17
```

__Trial 2:__
```text
Output:
Track 10 | Pedestrian | Speed=8.11 m/s | Avg Speed=6.71 m/s | History 17
Track 20 | Car | Speed=4.21 m/s | Avg Speed=5.40 m/s | History 17
Track 18 | Car | Speed=9.14 m/s | Avg Speed=5.43 m/s | History 17
Track 12 | Unknown | Speed=5.29 m/s | Avg Speed=5.05 m/s | History 17
Track 26 | Car | Speed=8.12 m/s | Avg Speed=5.26 m/s | History 17
Track 52 | Car | Speed=4.81 m/s | Avg Speed=5.09 m/s | History 15
Track 24 | Pedestrian | Speed=4.70 m/s | Avg Speed=4.81 m/s | History 17
Track 32 | Car | Speed=7.27 m/s | Avg Speed=6.08 m/s | History 17
Track 58 | Pedestrian | Speed=3.65 m/s | Avg Speed=3.13 m/s | History 14
Track 48 | Unknown | Speed=11.80 m/s | Avg Speed=9.67 m/s | History 16
Track 82 | Unknown | Speed=15.56 m/s | Avg Speed=5.45 m/s | History 12
Track 40 | Unknown | Speed=6.25 m/s | Avg Speed=5.05 m/s | History 17
```

__Trial 3:__
```text
Output:
Track 12 | Pedestrian | Speed=8.36 m/s | Avg Speed=6.73 m/s | History 17
Track 10 | Pedestrian | Speed=5.52 m/s | Avg Speed=5.37 m/s | History 17
Track 100 | Unknown | Speed=7.66 m/s | Avg Speed=5.31 m/s | History 10
Track 22 | Car | Speed=4.21 m/s | Avg Speed=5.40 m/s | History 17
Track 20 | Car | Speed=5.53 m/s | Avg Speed=5.27 m/s | History 17
Track 98 | Unknown | Speed=10.72 m/s | Avg Speed=7.91 m/s | History 10
Track 14 | Unknown | Speed=5.29 m/s | Avg Speed=5.05 m/s | History 17
Track 28 | Car | Speed=8.15 m/s | Avg Speed=5.15 m/s | History 17
Track 54 | Car | Speed=4.81 m/s | Avg Speed=5.09 m/s | History 15
Track 26 | Pedestrian | Speed=4.70 m/s | Avg Speed=4.81 m/s | History 17
Track 34 | Car | Speed=7.27 m/s | Avg Speed=5.92 m/s | History 17
Track 102 | Pedestrian | Speed=3.65 m/s | Avg Speed=3.17 m/s | History 10
Track 48 | Unknown | Speed=11.80 m/s | Avg Speed=9.67 m/s | History 16
Track 82 | Unknown | Speed=15.56 m/s | Avg Speed=5.45 m/s | History 12
Track 44 | Unknown | Speed=6.25 m/s | Avg Speed=5.05 m/s | History 17
```

__Trial 4:__
```text
Output:
Track 14 | Pedestrian | Speed=8.11 m/s | Avg Speed=6.71 m/s | History 17
Track 24 | Car | Speed=4.21 m/s | Avg Speed=5.41 m/s | History 17
Track 22 | Unknown | Speed=6.77 m/s | Avg Speed=5.19 m/s | History 17
Track 26 | Unknown | Speed=13.53 m/s | Avg Speed=6.81 m/s | History 17
Track 16 | Unknown | Speed=5.29 m/s | Avg Speed=5.05 m/s | History 17
Track 30 | Car | Speed=8.12 m/s | Avg Speed=6.02 m/s | History 17
Track 60 | Car | Speed=4.81 m/s | Avg Speed=5.09 m/s | History 15
Track 28 | Pedestrian | Speed=5.12 m/s | Avg Speed=4.85 m/s | History 17
Track 36 | Car | Speed=7.27 m/s | Avg Speed=6.04 m/s | History 17
Track 42 | Pedestrian | Speed=8.60 m/s | Avg Speed=4.06 m/s | History 17
Track 52 | Unknown | Speed=11.80 m/s | Avg Speed=9.67 m/s | History 16
Track 90 | Unknown | Speed=11.18 m/s | Avg Speed=5.43 m/s | History 12
Track 46 | Unknown | Speed=6.25 m/s | Avg Speed=5.05 m/s | History 17
```

After running the `run_phase_9.py` script with the updated average velocity estimation method multiple times, the results show that the average speeds for the tracked objects are more consistant and reasonable. However, for many of the trials, the second to last track in the output consistently showed a high instantaneous speed of approximately 11-15 m/s, while the average speed was significantly lower. This suggests that there may be a sudden change in the object's motion or a misclassification in the tracking data. Further analysis of the tracking data and the corresponding frames may be necessary to determine the cause of this discrepancy. Overall, the updated average velocity estimation methods provided a more accurate representation of the tracked objects' motion, especially for the tracks with longer histories.

## Conclusion
Velocity estimates were computed using each track's bounding-box center history. Instantaneous speed was calculated using the last two center positions, while average speed was computed using the accumulated frame-to-frame displacement over the full center-position history of each track.

The results show that long-lived car tracks produced relatively consistent average speeds, generally in the range of 4–5 m/s. Some pedestrian tracks produced speeds that were higher than expected for normal walking or running. These values are likely inflated due to ego-motion from the LiDAR sensor mounted on the moving vehicle, as well as center-estimation noise, bounding-box jitter, cluster splitting/merging, and object misclassification.

Overall, Phase 9 successfully demonstrated relative velocity estimation in the LiDAR coordinate frame using bounding-box center history. The results were visualized using Open3D, which helped evaluate tracking performance and velocity estimation. Further improvements could be made to improve accuracy and reliability. However, the current estimates should not be interpreted as absolute real-world velocities unless sensor ego-motion is compensated for.