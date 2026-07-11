import numpy as np

def polar_to_caresian(r, theta):
    """
    Convert polar coordinates to Cartesian coordinates.

    Parameters:
        r (float): The radial distance from the origin.
        theta (float): The angle in radians.
    
    Returns:
        x (float): The x-coordinate in Cartesian coordinates.
        y (float): The y-coordinate in Cartesian coordinates.
    """
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y