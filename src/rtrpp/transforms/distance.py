import numpy as np


def distances(xyz, axis):
    """
    Compute the Euclidean distances of points in a point cloud from the origin along a specified axis.

    Parameters:
        xyz (numpy.ndarray): The point cloud data as an Nx3 array.
        axis (int): The axis along which to compute the distances.

    Returns:
        numpy.ndarray: The Euclidean distances of the points along the specified axis.
    """
    distance = np.linalg.norm(xyz, axis)

    print("\nClosest point:", distance.min())
    print("Furthest point:", distance.max())
    print("Average distance:", distance.mean())
    return distance


def distances2(x, y, z):
    """
    Compute the Euclidean distances of points from the origin given their x, y, and z coordinates.

    Parameters:
        x (numpy.ndarray): The x-coordinates of the points.
        y (numpy.ndarray): The y-coordinates of the points.
        z (numpy.ndarray): The z-coordinates of the points.

    Returns:
        numpy.ndarray: The Euclidean distances of the points from the origin.
    """
    distance = np.sqrt(x**2 + y**2 + z**2)

    print("\nClosest point:", distance.min())
    print("Furthest point:", distance.max())
    print("Average distance:", distance.mean())
