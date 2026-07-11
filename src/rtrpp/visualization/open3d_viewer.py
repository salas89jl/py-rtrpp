import open3d as o3d
import time 


def animate_frames(frame_point_cloud, delay=0.1):

    """
    Animate a sequence of point cloud frames using Open3D.
    
    Parameters:
    frame_point_cloud (list): A list of Open3D point cloud objects representing the frames to be animateds
    delay (float): The time delay between frames in seconds. Default is 0.1 seconds.

    """
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="Frame Sequence")

    pcd = frame_point_cloud[0]
    vis.add_geometry(pcd)

    for frame_idx, frame_pcd in enumerate(frame_point_cloud):
        pcd.points = frame_pcd.points

        if frame_pcd.has_colors():
            pcd.colors = frame_pcd.colors
        
        vis.update_geometry(pcd)
        vis.poll_events()
        vis.update_renderer

        print(f"Showing frame {frame_idx}")
        time.sleep(delay)

    vis.destroy_window()

def animate_frames_with_boxes(frames, delay=0.2):

    """
    Animate a sequence of point cloud frames with bounding boxes using Open3D.

    Parameters:
    frames (list): A list of dictionaries, each containing a point cloud and its corresponding bounding
    boxes. Each dictionary should have the keys "pcd" (Open3D point cloud object) and "boxes" (list of Open3D bounding box objects).
    delay (float): The time delay between frames in seconds. Default is 0.2 seconds.
    """
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="Tracked KITTI Sequence")

    pcd = frames[0]["pcd"]
    boxes = frames[0]["boxes"]

    vis.add_geometry(pcd)

    for box in boxes:
        vis.add_geometry(box)

    current_boxes = boxes
    
    for frame_idx, frame in enumerate(frames):
        # Remove old boxes
        for box in current_boxes:
            vis.remove_geometry(box, reset_bounding_box=False)

        # Update point cloud
        pcd.points = frame["pcd"].points
        vis.update_geometry(pcd)

        # Add new boxes
        current_boxes = frame["boxes"]

        for box in current_boxes:
            vis.add_geometry(box, reset_bounding_box=False)


        # Update the visualizer and wait for the specified delay
        vis.poll_events()
        vis.update_renderer()

        print(f"Showing frame {frame_idx}") 

        time.sleep(delay)

    vis.destroy_window()