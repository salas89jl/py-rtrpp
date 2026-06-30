from src.io.loading import load_point_cloud
from src.preprocessing import outlier_filter, roi_filter, voxel_filter
from src.segmentation import dbscan_cluster, segment_ground

def run_pipeline(file_path):
    """
    Perception pipeline for LiDAR data
    
    Parameters:
        file_path: point cloud data file path
    
    Returns:
        object_points (open3d.geometry.PointCloud): The points belonging to the non-ground points. 
        labels: numpy array of shape(M,) containing cluster labels for each points
    """
    
    # Load point cloud from file path
    points = load_point_cloud(file_path)

    # Filter specific region
    roi_filtered = roi_filter.roi_filter(
        points,
        x_min=0, x_max=40,
        y_min=-20, y_max=20,
        z_min=-2, z_max=2
        )
    
    # Downsample only x, y and z filtered points
    downsampled = voxel_filter.downsample_point_cloud(
       xyz=roi_filtered[:, :3],
       voxel_size=0.2
    )

    # Remove outliers from downsampled points
    cleaned_points = outlier_filter.remove_outliers(
        downsampled, 
        nb_neighbors=20,
        std_ratio=2.0
    )

    # Segment ground and non-ground points
    ground_points, object_points = segment_ground.extract_segments(
        cleaned_points, 
        distance_threshold=0.2,
        ransac_n=3,
        num_iterations=1000
    )

    # Cluster non-ground points
    labels = dbscan_cluster.cluster_objects(
        object_points,
        eps=1.0,
        min_points=13
    )

    return object_points, labels