def roi_filter(points, x_min=-10, x_max=10, y_min=-10, y_max=10, z_min=-2, z_max=2):
    """
    Filter the point cloud to keep only points within a specified region of interest (ROI).
    
    Parameters:
    - points: A numpy array of shape (N, 4) containing the point cloud data (x, y, z, reflectance).
    - x_min, x_max: Minimum and maximum x coordinates for the ROI.
    - y_min, y_max: Minimum and maximum y coordinates for the ROI.
    - z_min, z_max: Minimum and maximum z coordinates for the ROI.
    
    Returns:
    - A numpy array of shape (M, 4) containing the filtered point cloud data within the ROI.
    """
    # Create a boolean mask to filter points within the specified ROI
    mask = (
        (points[:, 0] >= x_min) & (points[:, 0] <= x_max) &
        (points[:, 1] >= y_min) & (points[:, 1] <= y_max) &
        (points[:, 2] >= z_min) & (points[:, 2] <= z_max)
    )
    
    # Apply the mask to filter the points
    filtered_points = points[mask]
    
    return filtered_points