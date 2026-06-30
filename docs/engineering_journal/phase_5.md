# Object Clustering

In this phase, the goal is to take the non-ground red points and automatically group them into separate objects. This is a crucial step in the process of object detection and recognition, as it allows us to identify and classify individual objects in the point cloud data.

## Phase 5 Pipeline

Raw point cloud
```text
Raw point cloud
→ ROI filter
→ Downsample
→ Outlier removal
→ Ground plane extraction
→ DBSCAN clustering
```

## Density-Based Spatial Clustering of Applications (DBSCAN):
DBSCAN is an unsupervised machine learning clustering algorithm that groups data points together based on how closely packed the are. It only takes two paramters:
-  `Epsilon (ε)`: The radius or maximum distance to search for neighborng points around a target data point. 
-  `MinPts`: The minimum number of points (including the target point itself) required within the ε radius to form a dense region. 

### Three Types of Data Points
Based on the ε radius and MinPts settings, BDSCAN classifies every data point into onf three buckets:
1. __Core Points__: Points that have at least MinPtswithin their ε radius. These form the dense hearts of your cluster.
2. __Border Points__: Points that do not have enough neighbors to be a core point, but fall inside the ε radius of an existing corepoint. They sit on the outer edges of a cluster. 
3. __Noise Points__: Outliers that are neither core points nor border points. They are completely excluded from all custers. 

### How the Algorithm Works
1. __Desitity Check__: The algorithm picks an unvisited data point at random and counts how many points sit inside its ε radius. 
2. __Cluster Expansion__: If the point is a core point, a new cluster is created. Then the algorithm recursively pulls in all its neighbors. if any of those neighbors are also core points, their own neighborhoods join the cluster, expandings itshape. 
3. __Handle Edge & Noise__: If a point does not have enough neighbors it will be provisionally be labeled as noise. If it laters falls into a core point's radius, it will be upgraded to a border point inside that cluster. Otherwise, the point will remained labeled as noise. 
4. __Repeat__: This will repeat until every point in the dataset has been visited and classified. 
   
__Note__: An unsupervised learning model is a type of AI algorithm that learns patterns form data that has no labels, tags, or pre-defined answers. 


## Step 1: Create src/cluster_objects.py

```python
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
    labels = np.array(
        pcd.cluster_dbscan(
            eps=eps, 
            min_points=min_points
        )
    )

    return labels
```

## Extracting the Ground Plane
In autonomous drving datasets such as the KiTTi Dataset most of the objects that we are interested are cars, pedestrians, cyclist, poles, signs, etc. All of which sit on top of the road. If we removed the roat first, later object detection becomes alot easier. 

Instead of uses the process of least squares which is used to find the "best-fit" line or curve for set of data points by minimizing the sum of the sqred diffrences(residuals) to extract our plane. Note that if this process was used the resulting plane will be badly distored becuase the objects would act as outliers. To extract our plane we will use the Random Sample Consensus (RANSAC) method. 

The basic diea of RANSAC is to:
1. Randomly pick 3 points
2. Construct a plane through those points
3. Measure how many points agree with that plane
4. Repeat many times
5. Keep the plane with the largest agreement


### Why 3 Points
For a plane to be unique it requires 3 non-collinear points P1, P2, and P3. 

## RANSAC
## Step 2: Update Ground Extraction to Return Objects

In the `src/ground_extraction.py` file, update the `extract_ground` function to return both the ground points and the non-ground points (objects).

```python
def extract_ground(points, distance_threshold=0.2, ransac_n=3, num_iterations=1000):
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

    a, b, c, d = plane_model

    print(f"Plane model: {a:.2f}x + {b:.2f}y + {c:.2f}z + {d:.2f} = 0")

    return np.asarray(ground_points.points), np.asarray(objects.points)
```

## Step 3: Update Main Pipeline
Create a new file `run_phase_5.py` to run the entire pipeline for phase 5, including the new clustering step.

```python
import numpy as np
import open3d as o3d

from src.load_kitti import load_kitti_bin
from src.filter_roi import filter_roi
from src.down_sample import downsample_point_cloud
from src.remove_outliers import remove_outliers
from src.ground_plane import extract_ground_plane
from src.cluster_objects import cluster_objects


file_path = "datasets/kitti/0000000000.bin"

points = load_kitti_bin(file_path)

filtered_points = filter_roi(
    points,
    x_min=0,
    x_max=40,
    y_min=-20,
    y_max=20,
    z_min=-2,
    z_max=2
)

print("Number of points after ROI filtering:", len(filtered_points))

downsampled_points = downsample_point_cloud(
    filtered_points[:, :3],
    voxel_size=0.2
)

print("Points after downsampling:", len(downsampled_points))

cleaned_points = remove_outliers(
    downsampled_points,
    nb_neighbors=20,
    std_ratio=2.0
)

print("Points after outlier removal:", len(cleaned_points))

ground_points, object_points = extract_ground(
    cleaned_points,
    distance_threshold=0.2,
    ransac_n=3,
    num_iterations=1000
)

labels = cluster_objects(
    object_points,
    eps=0.8,
    min_points=15
)

num_clusters = labels.max() + 1
noise_points = np.sum(labels == -1)

print("Number of clusters:", num_clusters)
print("Noise points:", noise_points)
```
```text
Number of points after ROI filtering: 57643
Points after downsampling: 12716

Points after downsampling: 12716
Points after outlier removal: 12176

Points after outlier removal: 12176
Plane model: -0.00x + -0.00y + 1.00z + 1.60 = 0

Number of clusters detected: 45
Number of noise points: 220
```

## Step 4: Visualize Clusters
To visualize the clusters, you can use Open3D's visualization tools. Add the following code to the end of `run_phase_5.py`:

```python

max_label = labels.max()

colors = np.random.rand(max_label + 1, 3)
cluster_colors = np.zeros((len(labels), 3))

for i, label in enumerate(labels):
    if label == -1:
        cluster_colors[i] = [0, 0, 0]  # Noise points in black
    else:
        cluster_colors[i] = colors[label]

object_pcd = o3d.geometry.PointCloud()
object_pcd.points = o3d.utility.Vector3dVector(object_points)
object_pcd.colors = o3d.utility.Vector3dVector(cluster_colors)

ground_pcd = o3d.geometry.PointCloud()
ground_pcd.points = o3d.utility.Vector3dVector(ground_points)
ground_pcd.paint_uniform_color([0.5, 0.5, 0.5])  # Ground points in gray 

o3d.visualization.draw_geometries(
    [ground_pcd, object_pcd], 
    window_name="Phase 5: Object Clustering",

    
)
```
```text
Number of points after ROI filtering: 57643
Points after downsampling: 12716

Points after downsampling: 12716
Points after outlier removal: 12176

Points after outlier removal: 12176
Plane model: -0.01x + -0.00y + 1.00z + 1.61 = 0

Number of ground point: 6152
Number of non-ground points: 6024

Number of clusters detected: 35
Number of noise points: 341
```
<img src="/images/ph5_3d_grndRmvd_Cluster.png" alt="Visualization of a point cloud after clustering" style="width:600px; padding:10px;">


What the visualization shows is the result of the clustering process. We can clearly see distinct clusters corresponding to vehicles, poles, building facades, vegetation, and other objects in the scene. Each cluster is colored differently to help visually differentiate them. The ground points are shown in gray, while the clustered objects are shown in various colors. Noise points that were not assigned to any cluster are shown in black. This visualization allows us to see how well the DBSCAN algorithm was able to group the non-ground points into meaningful clusters based on their spatial proximity. We can see that DBSCAN was able to successfully identify and separate the different objects in the scene without need of labels or training data, demonstrating the power of unsupervised learning for point cloud clustering.

### Noise Clusters
The black points are noise points that were not assigned to any cluster. In this case, we can see that there are 341 noise points meaning that after the point cloud was downsampled and cleaned, there were 341 points out of the 6024 non-ground points that did not fit well into any of the clusters based on the DBSCAN parameters we set. This is about 5.65% of the total non-ground points, which is a reasonable amount of noise for a real-world LiDAR point cloud. These noise points could be caused by sensor inaccuracies, reflections, or other factors that result in points that do not belong to any meaningful cluster. Depending on the application, we may choose to ignore these noise points or further analyze them to see if they contain any useful information.

Note that several nearby cluster are over-segmented meaning that they are split into multiple clusters. This is a common issue with DBSCAN and can be addressed by adjusting the `eps` and `min_points` parameters to better capture the density of the clusters in the point cloud. This is completely normal for DBSCAN parameter setting eps=0.8. It may separate a vehicle body, its roof, and nearby points into separate clusters. Adjusting the parameters can help to merge these into a single cluster if desired, but it may also risk merging distinct objects together if set too high. Finding the right balance is key to achieving good clustering results.

Lets see what happens if we set `eps` to 1.0 instead of 0.8:

<img src="/images/ph5_3d_clustering_updated.png" alt="Visualization of a point cloud after clustering with eps=1.0" style="width:600px; padding:10px;">

```text
Number of points after ROI filtering: 57643
Points after downsampling: 12716

Points after downsampling: 12716
Points after outlier removal: 12176

Points after outlier removal: 12176
Plane model: -0.01x + -0.00y + 1.00z + 1.61 = 0

Number of ground point: 6090
Number of non-ground points: 6086

Number of clusters detected: 25
Number of noise points: 160
```

By increasing the `eps` parameter to 1.0, we can see that the number of clusters detected decreased from 35 to 25, and the number of noise points decreased from 341 to 160. This indicates that some of the previously over-segmented clusters have been merged together, resulting in fewer clusters overall. However, we can also see that some distinct objects may have been merged together as well, so it's important to carefully choose the `eps` parameter based on the specific characteristics of the point cloud and the desired level of clustering.

### Tuning DBSCAN Parameters
The choice of `eps` and `min_points` parameters can significantly affect the clustering results. Lets try setting `eps` to 0.5, 0.8, and 1.0 to see how it affects the number of clusters and noise points:

#### eps = 0.5
 <img src="/images/ph5_eps_0_5.png" alt="Visualization of a point cloud after clustering with eps=0.5" style="width:600px; padding:10px;">

```text
Number of ground point: 6298
Number of non-ground points: 5878

Number of clusters detected: 49
Number of noise points: 2217
```
#### eps = 0.8
<img src="/images/ph5_eps_0_8.png" alt="Visualization of a point cloud after clustering with eps=0.8" style="width:600px; padding:10px;">

```text
Number of ground point: 6236
Number of non-ground points: 5940

Number of clusters detected: 41
Number of noise points: 382
```
#### eps = 1.0
<img src="/images/ph5_eps_1_0.png" alt="Visualization of a point cloud after clustering with eps=1.0" style="width:600px; padding:10px;">

```text
Number of ground point: 5884
Number of non-ground points: 6292

Number of clusters detected: 25
Number of noise points: 104
```

|eps| Clusters Detected | Noise Points |
|---|-------------------|--------------|
|0.5| 49                | 2217         |
|0.8| 41                | 382          |
|1.0| 25                | 104          |    

These results are very informative. They show one of the most important tradeoffs in point cloud clustering: the balance between merging similar points together and keeping distinct objects separate. With a smaller `eps` value, we get more clusters but also more noise points, which can lead to over-segmentation. With a larger `eps` value, we get fewer clusters and fewer noise points, but we risk merging distinct objects together.

What DBSCAN is doing is essentially with a smaller `eps` value it is being more strict about which points belong to the same cluster. What likely happened is vehicles got split inot multiple clusters, many points could not find enough neighbors within the smaller radius and were labeled as noise. With a larger `eps` value, DBSCAN is being more lenient and allowing nearby objects to be merged together, which is why we see fewer clusters and fewer noise points. However, this also means that some distinct objects may have been merged together, which can be a problem if we want to accurately identify and classify individual objects in the scene. This is called under-segmentation, where distinct objects are merged into a single cluster. Finding the right balance between over-segmentation and under-segmentation is key to achieving good clustering results with DBSCAN. In practice, you may need to experiment with different `eps` and `min_points` values to find the best settings for your specific point cloud data and application. Additionally, you can also consider using other clustering algorithms or techniques to further refine the clusters and improve the results. 

Based on the results we have seen, an `eps` value of 0.8 seems to provide a good balance between the number of clusters detected and the number of noise points. It allows us to capture distinct objects in the scene while minimizing the amount of noise. However, the optimal `eps` value may vary depending on the specific characteristics of the point cloud data and the desired level of clustering, so it's important to experiment with different values to find the best settings for your application.

What this exercise demonstrates is the importance of parameter tuning in clustering algorithms like DBSCAN. The choice of parameters can significantly impact the results, and there is often a tradeoff between capturing distinct objects and minimizing noise. 

## What Have We Built So Far?
### Curent Pipeline
```text
Raw point cloud from KITTI .bin file
            ↓
ROI filter to focus on a specific region of interest
            ↓
Voxel downsampling to reduce the number of points while preserving the overall structure
            ↓
Outlier removal to clean the point cloud and remove noise
            ↓
Ground plane extraction using RANSAC to separate ground points from non-ground points
            ↓
DBSCAN clustering to group non-ground points into distinct clusters representing individual objects
```

This is already a very powerful pipeline for processing LiDAR point cloud data. We have taken raw point cloud data from the KITTI dataset and applied a series of processing steps to clean, downsample, and segment the data into meaningful clusters representing individual objects in the scene. The major difference between this pipeline and a full object detection pipeline is that production systems add object classification, tracking, sensor fusion, prediction, and other advanced features to create a complete autonomous driving solution. However, the pipeline we have built so far provides a solid foundation for understanding and working with LiDAR point cloud data in the context of autonomous driving and computer vision applications.

## Next Steps (Phase 6)
In the next phase, we will focus creating bounding boxes around the detected clusters to visualize and quantify the objects in the scene. This will involve calculating the minimum bounding box for each cluster and visualizing them in 3D space, allowing us to see how well our clustering algorithm has performed in identifying and separating individual objects.
