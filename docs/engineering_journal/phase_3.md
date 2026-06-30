# Phase 3 Filtering and Preprocessing
The goal of this phase is to filter and preprocess the LiDAR point cloud data to prepare it for further analysis. This includes removing noise, downsampling the point cloud, and extracting relevant features.

## Downsampling the Point Cloud
For the first step, we are going to reduce the number of points in the point cloud by applying a voxel grid filter. This will help to speed up subsequent processing steps while retaining the overall structure of the point cloud.

Downsampling is a technique used to reduce the number of points in a point cloud while preserving the overall structure and shape of the data. This is typically done by dividing the space into a grid of voxels (3D cubes) and replacing all points within each voxel with a single representative point, such as the centroid of the points in that voxel. This process helps to reduce the computational load and memory usage when working with large point clouds. 
### What is a Voxel?
A voxel is a 3D pixel. The word stands for "volumetric pixel" or "volume element". While a pixel represents a single point of data on a flat 2D grid (x and y coordinates), a voxel represents a value on a regular 3D grid (x, y, and z coordinates). 

### Key Characteristics of Voxels:
- **Volume Element:** A voxel represents a value in a 3D space, similar to how a pixel represents a value in a 2D space.
- **Position:** A voxel's position is not store as an explicit coordinate, but rather is inferred based on its relative location inside the larger 3D grid. The position of a voxel is determined by its index in the grid, which corresponds to its location in the 3D space.
- **Data Value:** Each voxel holds a specific data value. This value can represent various attributes, such as color or material properties, depending on the application. In the context of point clouds, a voxel might represent the average position of points within that voxel or other aggregated information about the points it contains.
- **Resolution:** The size of the voxels determines the resolution of the 3D representation. Smaller voxels can capture finer details but require more memory and computational power, while larger voxels provide a coarser representation but are more efficient to process.

### Real-World Applications:
- **Medical Imaging:** Voxels are commonly used in medical imaging techniques such as MRI and CT scans to represent 3D structures within the human body.
- **3D Graphics and Gaming:** Games like Minecraft build their entire worlds out of voxels, allowing for dynamic and destructible environments. In 3D graphics, voxels can be used to create volumetric effects like smoke, fire, and clouds.
- **Geospatial Analysis:** In geospatial applications, voxels can represent 3D terrain data, subsurface geological formations, or atmospheric phenomena.
- **Computer Vision and Robotics:** In robotics, voxels can be used for 3D mapping and navigation, allowing robots to understand and interact with their environment in three dimensions.


## Downsampling KiTTi Point Cloud Data:
In the KiTTi dataset, that we were working with contained a toltal of 122,160 points. Lets apply a voxel grid filter with a voxel size of 0.2 meters to downsample the point cloud. This will significantly reduce the number of points while preserving the overall shape and structure of the data.

```python
import open3d as o3d
def visualize_point_cloud(points, voxel_size=0.2):
    # Create an Open3D point cloud object
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    
    # Downsample the point cloud using a voxel grid filter
    if voxel_size > 0:
        pcd = pcd.voxel_down_sample(voxel_size=voxel_size)  # Adjust voxel size as needed
    
    # Visualize the downsampled point cloud
    o3d.visualization.draw_geometries(
        [pcd], 
        window_name="LiDAR Point Cloud Visualization",
    )
```

<img src="../images/ph3_3d_downSampling.png" alt="Downsampled Point Cloud Visualization" width="600">

Notice how the number of points has been significantly reduced while still maintaining the overall structure of the point cloud. This downsampled point cloud can now be used for further processing, such as feature extraction or object detection, with improved efficiency.

This matters because working with a smaller point cloud can significantly reduce the computational load and speed up subsequent processing steps, while still retaining the essential information needed for analysis. Instead of working with 122,160 points, we are now working with a much smaller set of points that still captures the overall structure of the scene, allowing us to perform tasks like object detection or segmentation more efficiently.

We can think of it as combining nearby points into small cubes called voxels, like 20 cm x 20 cm x 20 cm. Each voxel is represented by a single point, which helps to reduce the number of points while still keeping the overall shape of the data intact. This way, we can work with a more manageable number of points without losing important information about the scene.

## Filtering a Region of Interest (ROI)
In addition to downsampling, we can also filter the point cloud to focus on a specific region of interest (ROI). This is particularly useful when we are only interested in analyzing a specific area, such as the area 40 meters in front of the vehicle, 20 meterrs to the right and 20 meters to the left, and 2 meters above and below the LiDAR sensor.

```text
x ∈ [0, 40] meters
y ∈ [-20, 20] meters
z ∈ [-2, 2] meters
```
To filter the point cloud based on this ROI, we can use the following code that creates a mask to select only the points that fall within the specified ranges for x, y, and z coordinates:

```python   
def filter_roi(points, x_range=(0, 40), y_range=(-20, 20), z_range=(-2, 2)):
    # Create a mask to filter points within the specified ROI
    mask = (
        (points[:, 0] >= x_range[0]) & (points[:, 0] <= x_range[1]) &
        (points[:, 1] >= y_range[0]) & (points[:, 1] <= y_range[1]) &
        (points[:, 2] >= z_range[0]) & (points[:, 2] <= z_range[1])
    )
    return points[mask]
```

<img src="../images/ph3_3d_filteredROI.png" alt="ROI Filtered Point Cloud Visualization" width="600">

By applying this ROI filter, the number of points in the point cloud is further reduced, from a total of 122,160 points to 8,016 points. 

## Removing Outliers
In addition to downsampling and filtering the point cloud, we can also remove outliers to further clean the data. Outliers are points that do not fit well with the rest of the point cloud and can be caused by sensor noise or other factors. Removing outliers can help to improve the quality of the point cloud and make it easier to analyze.

To remove outliers, we can use a statistical outlier removal method that identifies and removes points that are significantly different from their neighbors. This can be done using the following code:

```python
def visualize_point_cloud_with_outliers_removed(xyz, nb_neighbors=20, std_ratio=2.0, voxel_size=None):
    """
    Visualize the point cloud with outliers removed using Open3D.
    """
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(xyz)
    
    # Remove outliers using statistical outlier removal
    pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
    
    if voxel_size is not None and voxel_size > 0:
        pcd = pcd.voxel_down_sample(voxel_size=voxel_size) # Downsample the point cloud for faster visualization
        print(
            "Points after downsampling:", 
            len(pcd.points)
        )
    
    o3d.visualization.draw_geometries(
        [pcd], 
        window_name="LiDAR Point Cloud Visualization (Outliers Removed)",
    )
    
```

<img src="../images/ph3_3d_outliersRemoved.png" alt="Outliers Removed Point Cloud Visualization" width="600">