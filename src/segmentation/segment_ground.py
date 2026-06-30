import open3d as o3d
import numpy as np

def extract_segments(points, distance_threshold=0.2, ransac_n=3, num_iterations=1000):
    """Extract ground points from the input point cloud.

    Parameters:
        points: numpy array of shape (N, 3)
        distance_threshold: maximum distance a point can be from the plane to be considered an inlier
        ransac_n: number of points to sample for plane fitting
        num_iterations: number of iterations for RANSAC

    Returns:
        ground_points: numpy array of shape (M, 3) containing ground points
        non_ground_points: numpy array of shape (K, 3) containing non-ground points
    """

    # Create an Open3D point cloud from the input points
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    # Perform RANSAC plane fitting
    plane_model, inliers = pcd.segment_plane(
        distance_threshold=distance_threshold,
        ransac_n=ransac_n,
        num_iterations=num_iterations
    )

    # Extract ground and non-ground points
    ground_points = pcd.select_by_index(inliers)
    objects = pcd.select_by_index(inliers, invert=True)

    return np.asarray(ground_points.points), np.asarray(objects.points)

