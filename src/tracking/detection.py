import numpy as np
import open3d as o3d

from src.segmentation.object_classification import simple_classification
from src.segmentation.bounding_box import compute_bounding_box

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


    def __str__(self):
        return(
            f"Cluster {self.cluster_id}: {self.classification} | "
            f"Center=({self.center[0]:.2f}, {self.center[1]:.2f}, {self.center[2]:.2f}) | "
            f"L={self.length:.2f}, W={self.width:.2f}, H={self.height:.2f}, "
            f"V={self.volume:.2f}"
        )
    


def detected_bounding_boxes(object_points, labels):
    """
    Generate bounding boxes for detected clusters of points.

    Parameters:
        object_points (numpy.ndarray): A 2D array of shape (N, 3) containing the x, y, z coordinates of the object points.
        labels (numpy.ndarray): A 1D array of shape (N,) containing the cluster labels for each point in object_points.

    Returns:
        list: A list of Detection objects representing the detected bounding boxes.
    """
    bounding_boxes = []

    unique_labels = np.unique(labels)

    for cluster_id in unique_labels:
        if cluster_id == -1:
            continue
        # filter through the object points to get the points that belong to the current cluster
        cluster_points = object_points[labels == cluster_id]

        # Skip clusters with too few points to avoid noise
        if len(cluster_points) < 20:
            continue

        # Compute the bounding box dimensions for analysis
        box = compute_bounding_box(cluster_points)       
        
        # classify all of the object clusters based on box dimensions
        label = simple_classification(
            box["length"],
            box["width"],
            box["height"]
        )

        # Create a point cloud object for the current cluster
        pcd_cluster = o3d.geometry.PointCloud()
        pcd_cluster.points = o3d.utility.Vector3dVector(cluster_points)

        # Compute the axis-aligned bounding box for the current cluster
        bbox = pcd_cluster.get_axis_aligned_bounding_box()
        bbox.color = get_label_color(label) # Set bounding box color to red

        # Print classification
        center = bbox.get_center()

        # create detection object
        detection = Detection(cluster_id, label, center, bbox, box["length"], box["width"],box["height"])

        # Append the bounding box to the list of bounding boxes
        bounding_boxes.append(detection)

    return bounding_boxes

def get_label_color(label):
    """
    Get the color associated with a given classification label.

    Parameters:
        label (str): The classification label ("Car", "Pedestrian", "Cyclist", or "Unknown").

    Returns:
        list: A list of three floats representing the RGB color.
    """

    if label == "Car":
        return [1, 0, 0]      #red
    elif label == "Pedestrian":
        return [0, 1, 0]    # green
    elif label == "Cyclist":
        return [0, 0, 1]   # blue
    else: 
        return [0, 0, 0]    # black
    
def get_box_volume(length, width, height):
    """
    Calculate the volume of a bounding box given its dimensions.

    Parameters:
        length (float): The length of the bounding box.
        width (float): The width of the bounding box.
        height (float): The height of the bounding box.

    Returns:
        float: The volume of the bounding box.
    """
    return length * width * height