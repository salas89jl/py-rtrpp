import numpy as np
import open3d as o3d


def cluster_objects(points, eps=0.7, min_points=10):
    """Cluster the input points using DBSCAN algorithm.

    Parameters:
        points: numpy array of shape (N, 3)
        eps: maximum distance between neighboring points in a cluster
        min_points: minimum points needed to form a cluster

    Returns:
        labels: numpy array of shape (N,) containing cluster labels for each point
    """

    # Create an Open3D point cloud from the input points
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    # Perform DBSCAN clustering
    labels = np.array(pcd.cluster_dbscan(eps=eps, min_points=min_points))

    return labels
