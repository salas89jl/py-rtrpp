import open3d as o3d
from pathlib import Path
from rtrpp.pipeline.pipeline import run_pipeline
from rtrpp.tracking import tracking
from rtrpp.tracking.detection import detected_bounding_boxes
from rtrpp.visualization.open3d_viewer import animate_frames_with_boxes


def run_offline_lidar_pipeline(module_path):
    """
    Run the offline LiDAR pipeline on a sequence of point cloud frames stored in binary files.
    
    Parameters:
    module_path (str): The path to the directory containing the binary files representing the point cloud frames.
    
    This function processes each binary file in the specified directory, detects objects based on bounding box dimensions,
    and visualizes the results using Open3D. The detected objects are tracked across frames, and the bounding boxes are displayed in the visualization.
    """
    tracker = tracking.SimpleTracker()

    frame_files = sorted(
        Path(module_path).glob("*bin")
    )

    print(len(frame_files))
    frames = []

    for frame_idx, file_path in enumerate(frame_files):
        object_points, labels = run_pipeline(file_path)
        
        
        # Detect objects based on bounding box dimensions in the current frame
        detections = detected_bounding_boxes(
            object_points,
            labels
        )

        # Update tracking system with current frame's detections
        tracked_objects = tracker.update(detections)

        # Create a point cloud object for the object points in current frame
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(object_points[:, :3])

        boxes = []

        # Retrieve all bounding box Open3D objects from all detections for visualization
        for detection in detections:
            bbox = detection.bbox
            bbox.color = [1, 0, 0]
            boxes.append(bbox)

        frames.append({
            "pcd": pcd,
            "boxes": boxes
        })


    for track in list(tracker.tracks.values()):
        if track.frames_seen >= 10:
            print(track)


    animate_frames_with_boxes(frames, delay=0.3)