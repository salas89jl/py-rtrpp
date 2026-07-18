import numpy as np


def compute_bounding_box(cluster_points):
    """
    Compute the axis-aligned bounding box for a given cluster of points.

    Parameters:
        cluster_points (numpy.ndarray): A 2D array of shape (N, 3) containing the x, y, z coordinates of the points in the cluster.

    Returns:
        dict: A dictionary containing the bounding box parameters:
            - "xmin", "xmax": Minimum and maximum x coordinates.
            - "ymin", "ymax": Minimum and maximum y coordinates.
            - "zmin", "zmax": Minimum and maximum z coordinates.
            - "length": Length of the bounding box (max of x and y dimensions).
            - "width": Width of the bounding box (min of x and y dimensions).
            - "height": Height of the bounding box (zmax - zmin).
    """
    xmin = np.min(cluster_points[:, 0])
    xmax = np.max(cluster_points[:, 0])

    ymin = np.min(cluster_points[:, 1])
    ymax = np.max(cluster_points[:, 1])

    zmin = np.min(cluster_points[:, 2])
    zmax = np.max(cluster_points[:, 2])

    dim1 = xmax - xmin
    dim2 = ymax - ymin

    length = max(dim1, dim2)
    width = min(dim1, dim2)
    height = zmax - zmin

    return {
        "xmin": xmin,
        "xmax": xmax,
        "ymin": ymin,
        "ymax": ymax,
        "zmin": zmin,
        "zmax": zmax,
        "length": length,
        "width": width,
        "height": height,
    }
