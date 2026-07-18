import numpy as np
import open3d as o3d


def remove_outliers(points, nb_neighbors=20, std_ratio=2.0):
    """Remove outliers from the point cloud using statistical outlier removal.
    Parameters:
    - points: A numpy array of shape (N, 3) containing the point cloud data (x, y, z).
    - nb_neighbors: Number of neighbors to analyze for each point.
    - std_ratio: Standard deviation ratio for the distance threshold.
    Returns:
    - A numpy array of shape (M, 3) containing the filtered point cloud data after outlier removal.
    """
    # Create an Open3D point cloud object
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    # Remove outliers using statistical outlier removal
    pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)

    # print(
    #     "Points after outlier removal:",
    #     len(pcd.points)
    # )
    return np.asarray(pcd.points)
