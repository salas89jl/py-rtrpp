import numpy as np


def load_point_cloud(file_path):
    """
    Load a point cloud from a binary file.

    Parameters:
        file_path (str): The path to the binary file.

    Returns:
        points (numpy.ndarray): A 2D array of shape (N, 4) containing the point cloud data, where N is the number of points.
        Each row contains [x, y, z, intensity] for a point in the point cloud.
    """
    points = np.fromfile(file_path, dtype=np.float32)
    points = points.reshape(-1, 4)

    return points
