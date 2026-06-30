# Phase 2 Load and Visualize real point-coud data

In this phase, we will use KITTI dataset as the first real dataset. The KITTI dataset is a popular dataset for autonomous driving research and contains a variety of data, including LiDAR point clouds, images, and GPS/IMU data. This includes Velodyne LiDAR scans, which provide 3D point cloud data of the environment around the vehicle. And, Open3D can be used to visualize the point cloud data because it can read point-cloud formats like .pcd and .ply, which are commonly used for storing point cloud data.

## Step 1: Folder Structure
```text
lidar-project/
├── datasets/
│   └── kitti/
├── src/
│   ├── __init__.py
│   ├── coordinates.py
│   ├── synthetic_scans.py
│   ├── plot_utils.py
│   └── load_kitti.py
├── run_phase2.py   
└── README.md  
```

## Step 2: Load KITTI Point Cloud Data
To load the KITTI point cloud data, we can create a new file named load_kitti.py in the src/ directory. This file will contain a function that reads the point cloud data from the KITTI dataset and returns it in a format that can be used for visualization.

An example of KITTI point cloud data set can be found in the following link: [KITTI Dataset](http://www.cvlibs.net/datasets/kitti/). You can download the Velodyne point cloud data from the KITTI dataset and place it in the datasets/kitti/ directory.

```python
import numpy as np

def load_kitti_bin(file_path):
    """
    KITTI Velodyne .bin files store points as:
    x, y, z, reflectance
    """
    points = np.fromfile(file_path, dtype=np.float32)
    print(f"Loaded {len(points) // 4} points from {file_path}")
    print(f"Raw data shape: {points.shape}")
    print(f"First 5 raw values: {points[:20]}")  # Print the first 5 points (20 values)
    points = points.reshape(-1, 4)
    print(f"Reshaped data shape: {points.shape}")
    print(f"First 5 points after reshaping:\n{points[:5]}")
    return points
```
```text
Loaded 122160 points from datasets/kitti/0000000000.bin
Raw data shape: (488640,)
First 5 raw values: [65.428  4.049  2.426  0.    65.74   4.483  2.437  0.    65.783  4.59
  2.439  0.    65.812  4.8    2.44   0.    65.844  5.01   2.442  0.   ]
Reshaped data shape: (122160, 4)
First 5 points after reshaping:
[[65.428  4.049  2.426  0.   ]
 [65.74   4.483  2.437  0.   ]
 [65.783  4.59   2.439  0.   ]
 [65.812  4.8    2.44   0.   ]
 [65.844  5.01   2.442  0.   ]]
```
### Understanding the `load_kitti_point_cloud` function:
The function `load_kitti_point_cloud` takes a file path as input, which points to a .bin file containing the Velodyne point cloud data from the KiTTi dataset. Using the Numpy library, it reads the binary data and reshapes it into a 2D array where each row corresponds to a point in the point cloud, and each column corresponds to the x, y, z coordinates and reflectance value. The function then returns only the x, y, and z coordinates of the points, which can be used for visualization and further processing.

## Step 3: Create run_phase2.py to Load and Visualize the Point Cloud
Next, we can create a run_phase2.py file that will use the load_kitti.py file to load the point cloud data and then use the plot_utils.py file to visualize it.
```python

from src.load_kitti import load_kitti_bin
from src.plot_utils import plot_2d_points


file_path = "datasets/kitti/0000000000.bin"

points = load_kitti_bin(file_path)

x = points[:, 0]
y = points[:, 1]
z = points[:, 2]
reflectance = points[:, 3]

print("Number of points", len(points))

print("Shape:", points.shape)


print("Frist 5 points: ")
print(points[5])

plot_2d_points(x, y,"KITTI LiDAR Scan: Top-Down View")
```

### Understanding the Data:
The point cloud data from the KITTI dataset is stored in .bin files, where each point is represented by four values: x, y, z coordinates and reflectance. The x, y, and z values represent the 3D position of each point in space, while the reflectance value indicates the intensity of the return signal from the LiDAR sensor.

Each row is [x, y, z, reflectance], where:
- x: The x-coordinate of the point in meters.
- y: The y-coordinate of the point in meters.
- z: The z-coordinate of the point in meters.
- reflectance: The intensity of the return signal, which can be used to determine the reflectivity of the surface that the LiDAR beam hit. Higher reflectance values indicate more reflective surfaces, while lower values indicate less reflective surfaces.

KiTTi uses the Velodyne coordinate frame, where:
- The x-axis points forward (in the direction the vehicle is facing) and backwards.
- The y-axis points to the left and right of the vehicle.
- The z-axis points upwards.
- The origin (0, 0, 0) is typically located at the center of the LiDAR sensor on the vehicle.
  
If we wanted to visualize it mentally, we can imagine the point cloud as a 3D scatter plot where each point represents a location in space. The x and y coordinates determine the horizontal position of the points, while the z coordinate determines their vertical position. The reflectance value can be used to color the points based on their intensity, which can help to differentiate between different surfaces and objects in the environment.

## Exloring the Point Cloud Data
After loading the point cloud data, we can explore it by printing out the number of points, the shape of the data, and the first few points. This can help us understand the structure of the data and how it is organized. We can also visualize the point cloud using a top-down view, which can provide insights into the layout of the environment around the vehicle.

```python
import numpy as np
from src.load_kitti import load_kitti_bin
from src.plot_utils import plot_2d_points


file_path = "datasets/kitti/0000000000.bin"

points = load_kitti_bin(file_path)
# We can extract a specific column from the 2D array using NumPy array slicing point[:, column_index]
x = points[:, 0]
y = points[:, 1]
z = points[:, 2]
reflectance = points[:, 3]

print("Number of points", len(points))

print("\nMinimum and maximum values for x, y, z:")
print("x: min =", np.min(x), ", max =", np.max(x))
print("y: min =", np.min(y), ", max =", np.max(y))
print("z: min =", np.min(z), ", max =", np.max(z))
print("\nFirst 5 points: ")
print(points[:5])
```

```text
Number of points 122160

Minimum and maximum values for x, y, z:
x: min = -79.731 , max = 79.198
y: min = -64.27 , max = 42.601
z: min = -5.311 , max = 2.89

First 5 points: 
[[65.428  4.049  2.426  0.   ]
 [65.74   4.483  2.437  0.   ]
 [65.783  4.59   2.439  0.   ]
 [65.812  4.8    2.44   0.   ]
 [65.844  5.01   2.442  0.   ]]
```

Alternatively, we can use:
```python
xyz = points[:, :3]

print("\nNumber of points:", len(xyz))

print("\nMinimum coordinates:")
print(xyz.min(axis=0))

print("\nMaximum coordinates:")
print(xyz.max(axis=0))
``` 
```text
Number of points: 122160
Minimum coordinates:
[-79.731  -64.27   -5.311]
Maximum coordinates:
[ 79.198   42.601    2.89 ]
```
__Note__: The number of points and the range of coordinates can vary depending on the specific scan and the environment it was captured in. The values provided here are just an example based on a single scan from the KITTI dataset. 

In this example scan, we have 122,160 points, with x coordinates ranging from -79.731 to 79.198 meters, y coordinates ranging from -64.27 to 42.601 meters, and z coordinates ranging from -5.311 to 2.89 meters. This indicates that the point cloud captures a wide area around the vehicle, with points representing objects and surfaces at various distances and heights. The minimum and maximum values for x, y, and z can help us understand the spatial extent of the point cloud and the distribution of points in the environment. For example, a large range in x and y coordinates may indicate that the scan captures a wide area, while a smaller range in z coordinates may suggest that most points are close to the ground or at a similar height.

## Distiance Analysis
We can also analyze the distance of the points from the LiDAR sensor. The distance can be calculated using the Euclidean distance formula, which is given by:
distance = sqrt(x^2 + y^2 + z^2)

```python
import numpy as np
from src.load_kitti import load_kitti_bin   
file_path = "datasets/kitti/0000000000.bin"
points = load_kitti_bin(file_path)
x = points[:, 0]
y = points[:, 1]
z = points[:, 2]
distances = np.sqrt(x**2 + y**2 + z**2)
print("\nClosest point:", distances.min())
print("Furthest point:", distances.max())
print("Average distance:", distances.mean())
```

```text
Closest point: 1.4604245
Furthest point: 79.9709
Average distance: 14.115864
```
In this example, the closest point in the point cloud is approximately 1.46 meters away from the LiDAR sensor, while the furthest point is approximately 79.97 meters away. The average distance of the points from the sensor is approximately 14.12 meters. This information can be useful for understanding the distribution of points in the point cloud and for identifying objects that are close to or far from the vehicle. For example, points that are very close to the sensor may represent nearby objects or surfaces, while points that are far away may represent distant objects or terrain features. Analyzing the distance of points can also help in tasks such as object detection and tracking, where the distance of points can be used to estimate the size and position of objects in the environment. 

### Creating a Histogram of Distances
We can also create a histogram of the distances to visualize the distribution of points in terms of their distance from the LiDAR sensor. This can help us understand how many points are close to the sensor and how many are far away.
```python
import matplotlib.pyplot as plt
plt.hist(distances, bins=50, range=(0, 80))
plt.title("Histogram of Distances from LiDAR Sensor")
plt.xlabel("Distance (meters)")
plt.ylabel("Number of Points")
plt.show()
```

<img src="/images/ph2_hist.png" alt="Histogram of Distances from LiDAR Sensor" width="400"/>

This code will create a histogram with 50 bins, showing the distribution of distances from the LiDAR sensor. The x-axis will represent the distance in meters, while the y-axis will represent the number of points that fall within each distance bin. This visualization can help us identify patterns in the data, such as whether there are more points close to the sensor or if there is a significant number of points at certain distance ranges, which can be indicative of the environment being scanned (e.g., urban vs. rural).

## First 3D Visualization
To visualize the point cloud data in 3D, we can use the Open3D library, which provides powerful tools for working with 3D data. We can create a simple 3D scatter plot of the point cloud data to get a better understanding of the spatial distribution of the points in three-dimensional space. Here's how you can do it:

```python
import open3d as o3d
def visualize_point_cloud(points):
    # Create an Open3D point cloud object
    pcd = o3d.geometry.PointCloud()
    
    # Set the points of the point cloud
    pcd.points = o3d.utility.Vector3dVector(points)
    
    # Visualize the point cloud
    o3d.visualization.draw_geometries([pcd])
```
In this function, we create an Open3D point cloud object and set its points using the input data. We then call the draw_geometries function to visualize the point cloud. You can call this function with the x, y, z coordinates of the points to see the 3D visualization of the KITTI LiDAR scan.

<img src="/images/ph2_3dVisual.png" alt="3D Visualization of KITTI LiDAR Scan" width="400"/>


In the image above, we can see a 3D visualization of the KITTI LiDAR scan. The points are colored based on their reflectance values, which can help to differentiate between different surfaces and objects in the environment. The x, y, and z axes represent the spatial coordinates of the points in three-dimensional space, allowing us to see the structure of the environment around the vehicle. This type of visualization can be very useful for understanding the layout of the scene and for identifying objects and features in the point cloud data.

