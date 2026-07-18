import numpy as np
import open3d as o3d


def downsample_point_cloud(xyz, voxel_size):
    """
    Downsample the point cloud using a voxel grid filter.

    Parameters:
        xyz (numpy.ndarray): A 2D array of shape (N, 3) containing the x, y, z coordinates of the point cloud.
        voxel_size (float): The size of the voxel grid for downsampling. Points within each voxel will be replaced by their centroid.

    Returns:
        downsampled_points (numpy.ndarray): A 2D array of shape (M, 3) containing the downsampled point cloud, where M is the number of points after downsampling.
    """
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(xyz)

    # Downsample the point cloud using a voxel grid filter if voxel_size is provided and greater than 0
    if voxel_size is not None and voxel_size > 0:
        pcd = pcd.voxel_down_sample(voxel_size=voxel_size)

        # print(
        #     "Points after downsampling:",
        #     len(pcd.points)
        # )

    return np.asarray(pcd.points)
