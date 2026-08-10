# Phase 6: Bounding Box Detection and Visualization
In this phase, we will visualize the bounding boxes around detected objects in the LiDAR point cloud data. Bounding boxes are used to represent the spatial extent of objects in 3D space and are essential for tasks such as object detection and tracking.

For each cluster we will find all of the points that belong to that cluster and compute the minimum and maximum coordinates along each axis (x, y, z). These coordinates will define the corners of the bounding box. We will then visualize the bounding boxes along with the point cloud data to see how well they encapsulate the detected objects. 

## Why this is Important
In autonomous driving and computer vision applications, it is not only important to detect objects, but also to understand their spatial extent such as position, size, and orientation. Bounding boxes provide a simple yet effective way to represent this information. By visualizing bounding boxes around detected clusters, we can assess the performance of our clustering algorithm and gain insights into the characteristics of the objects in the scene. Building a bounding boxes visualization pipeline is a crucial step towards developing a complete object detection, tracking, and classification system for autonomous vehicles. Because they need information such as:

|__Object__|__Position (x, y, z)__|__Width__|__Length__|__Height__|__Orientation__|
|:---:|:---:|:---:|:---:|:---:|:---:|
|Car| (12.3, -2.1, 0.5) | 1.8 m | 4.5 m | 1.5 m | 0.0 rad |
|Pedestrian| (8.5, 1.2, 0.0) | 0.6 m | 0.6 m | 1.8 m | 0.5 rad |

## Steps to building Bounding Boxes

For each cluster, we will:
1. Compute and Analyze the Bounding Box Dimensions
<!-- 2. Create a Bounding Box Object -->
2. Process All Clusters
3. Create bounding boxes for each cluster
4. Visualize Bounding Boxes

## Step 1: Compute and Analyze the Bounding Box Dimensions
To compute the bounding box dimensions for a given cluster, we will find the minimum and maximum coordinates along each axis (x, y, z) for all the points in that cluster. The minimum coordinates will define one corner of the bounding box, while the maximum coordinates will define the opposite corner.

Recall that we have already implemented a function that extracts clusters from the point cloud data using the DBSCAN algorithm and returns a list of clusters, where each cluster is a list of points. We can use this function to get the points for each cluster and then compute the bounding box dimensions.    

```python
def compute_bounding_box(cluster_points):

    xmin = np.min(cluster_points[:, 0])
    xmax = np.max(cluster_points[:, 0])

    ymin = np.min(cluster_points[:, 1])
    ymax = np.max(cluster_points[:, 1])

    zmin = np.min(cluster_points[:, 2])
    zmax = np.max(cluster_points[:, 2])

    # Return the bounding box dimensions as a dictionary
    return {
        "xmin": round(xmin, 6),
        "xmax": round(xmax, 6),
        "ymin": round(ymin, 6),
        "ymax": round(ymax, 6),
        "zmin": round(zmin, 6),
        "zmax": round(zmax, 6),
        "length": round(xmax - xmin, 6),
        "width": round(ymax - ymin, 6),
        "height": round(zmax - zmin, 6),
    }
```
In this function, we take the points of a cluster as input and compute the minimum and maximum coordinates along the x, y, and z axes. We also calculate the length, width, and height of the bounding box based on these coordinates. 

## Step 2: Process All Clusters
Now that we have a function to compute the bounding box dimensions for a single cluster, we can process all clusters in the point cloud data. We will iterate through each cluster, compute its bounding box dimensions, and store the results in a list for further analysis and visualization. If a cluster is labeled as noise (i.e., cluster_id == -1), we will skip it since it does not represent a valid object. Then, we will create a varible called `cluster_points` to store the points of the current cluster by filtering the original ground_points array based on the cluster labels. Finally, we will call the `compute_bounding_box` function to calculate the bounding box dimensions for the current cluster and append the result to a list called `bounding_boxes`.

```python
for cluster_id in np.unique(labels):
    if cluster_id == -1:
        continue  # Skip noise points

    cluster_points = ground_points[labels == cluster_id]
    bounding_box = compute_bounding_box(cluster_points)
    bounding_boxes.append(bounding_box)
```

```text
Cluster 0
{'xmin': np.float64(2.648364), 'xmax': np.float64(8.399625), 'ymin': np.float64(-2.855182), 'ymax': np.float64(1.440077), 'zmin': np.float64(-1.751667), 'zmax': np.float64(-1.68275), 'length': np.float64(5.751261), 'width': np.float64(4.295259), 'height': np.float64(0.068917)}

Cluster 1
{'xmin': np.float64(0.009), 'xmax': np.float64(17.309999), 'ymin': np.float64(-19.983999), 'ymax': np.float64(-3.881), 'zmin': np.float64(-1.296), 'zmax': np.float64(0.908), 'length': np.float64(17.300999), 'width': np.float64(16.102999), 'height': np.float64(2.204)}

Cluster 2
{'xmin': np.float64(5.041), 'xmax': np.float64(6.607778), 'ymin': np.float64(6.641333), 'ymax': np.float64(10.1535), 'zmin': np.float64(-1.2835), 'zmax': np.float64(-0.049875), 'length': np.float64(1.566778), 'width': np.float64(3.512167), 'height': np.float64(1.233625)}

Cluster 3
{'xmin': np.float64(13.7685), 'xmax': np.float64(14.933), 'ymin': np.float64(-1.832), 'ymax': np.float64(-1.253), 'zmin': np.float64(-1.26), 'zmax': np.float64(0.04725), 'length': np.float64(1.1645), 'width': np.float64(0.579), 'height': np.float64(1.30725)}

Cluster 4
{'xmin': np.float64(0.044333), 'xmax': np.float64(14.737), 'ymin': np.float64(14.2745), 'ymax': np.float64(19.986), 'zmin': np.float64(-1.283), 'zmax': np.float64(0.947), 'length': np.float64(14.692667), 'width': np.float64(5.7115), 'height': np.float64(2.23)}

Cluster 5
{'xmin': np.float64(11.221834), 'xmax': np.float64(11.52), 'ymin': np.float64(7.7812), 'ymax': np.float64(8.157), 'zmin': np.float64(-1.21775), 'zmax': np.float64(0.6295), 'length': np.float64(0.298167), 'width': np.float64(0.3758), 'height': np.float64(1.84725)}
```

This output shows the bounding box dimensions for only the first 6 clusters, and the total number of clusters is 22 for this case. The bounding box dimensions include the minimum and maximum coordinates along each axis, as well as the length, width, and height of the bounding box.

## Step 3: Create Bounding Boxes for Each Cluster
Now that we have computed the bounding box dimensions for each cluster, we can create bounding box objects using Open3D's `get_axis_aligned_bounding_box` method. This method takes a point cloud as input and returns an axis-aligned bounding box that encapsulates the points in the cluster. We will iterate through each cluster, create a point cloud object for the cluster points, and then compute the bounding box for that cluster. We will also set the color of the bounding box to red for better visualization.

```python
def create_bounding_boxes(object_points, labels):
    bounding_boxes = []

    unique_labels = np.unique(labels)

    for cluster_id in unique_labels:
        if cluster_id == -1:
            continue
        # filter through the object points to get the points that belong to the current cluster
        cluster_points = object_points[labels == cluster_id]

        # Skip clusters with too few points to avoid noise
        if len(cluster_points) < 20:
            continue

        # Create a point cloud object for the current cluster
        pcd_cluster = o3d.geometry.PointCloud()
        pcd_cluster.points = o3d.utility.Vector3dVector(cluster_points)

        # Compute the axis-aligned bounding box for the current cluster
        bbox = pcd_cluster.get_axis_aligned_bounding_box()
        bbox.color = [1, 0, 0]  # Set bounding box color to red

        # Compute the bounding box dimensions for analysis
        box = compute_bounding_box(cluster_points)
        print(f"\nCluster {cluster_id}")
        print(box)

        # Append the bounding box to the list of bounding boxes
        bounding_boxes.append(bbox)

    return bounding_boxes
```
In this function, we iterate through each unique cluster label, create a point cloud object for the points in that cluster, and compute the axis-aligned bounding box. We also print the bounding box dimensions for each cluster for analysis. Finally, we return a list of bounding box objects that can be visualized along with the original point cloud data.

## Step 4: Visualize Bounding Boxes
In the final step, we will visualize the bounding boxes along with the clustered point cloud data. We will create an Open3D point cloud object for the clustered points and assign a random color to each cluster for better visualization. We will then use Open3D's visualization capabilities to display the point cloud along with the bounding boxes.

```python
def visualize_with_bounding_boxes(labels, object_points, ground_points):
    # Calculate the number of clusters detected and the number of noise points ( points labeled as -1)
    num_clusters = labels.max() + 1
    noise_points = object_points[labels == -1]

    # Assign a random color to each cluster
    colors = np.random.rand(num_clusters, 3)
    cluster_colors = np.zeros((len(labels), 3))
    for i, label in enumerate(labels):
        if label == -1:
            cluster_colors[i] = [0, 0, 0]  # Noise points in black
        else:
            cluster_colors[i] = colors[label]

    # Create Open3D point clouds for the clustered object points
    object_pcd = o3d.geometry.PointCloud()
    object_pcd.points = o3d.utility.Vector3dVector(
        object_points
    )  # Set the points of the point cloud to the clustered object points
    object_pcd.colors = o3d.utility.Vector3dVector(
        cluster_colors
    )  # Set the colors of the point cloud to the assigned cluster colors

    # Create an array of axis-aligned bounding boxes for each cluster
    bounding_boxes = create_bounding_boxes(object_points, labels)

    # Visualize the Open3d point clouds
    o3d.visualization.draw_geometries([object_pcd] + bounding_boxes)
```
<img src="/images/ph6_3d_img_bbox.png" alt="3D Point Cloud with Bounding Boxes" width="600"/>

## Effect of `eps` Parameter on Clustering and Bounding Boxes
The visualization of the 3D point cloud with bounding boxes allows us to clearly see the spatial distribution of the clusters and their corresponding bounding boxes. But, how does the DBSCAN algorithm's `eps` parameter affect the number and size of the detected clusters and their bounding boxes? Lets run the DBSCAN algorithm with different `eps` values and observe the changes in the number of clusters, their sizes, and the corresponding bounding boxes.

#### `eps = 0.5`
<img src="/images/ph6_eps_0_5.png" alt="DBSCAN with eps=0.5" width="600"/>

The number of clusters detected with `eps = 0.5` that are greater than 20 points is 39. 

#### `eps = 0.8`
<img src="/images/ph6_eps_0_8.png" alt="DBSCAN with eps=0.8" width="600"/>

The number of clusters detected with `eps = 0.8` that are greater than 20 points is 31.

#### `eps = 1.0`
<img src="/images/ph6_eps_1_0.png" alt="DBSCAN with eps=1.0" width="600"/>  

The number of clusters detected with `eps = 1.0` that are greater than 20 points is 26.

Lets compare these results with the actual image from the dataset to see how well the clusters and bounding boxes correspond to the objects in the scene.

<img src="/images/0000000000.png" alt="Actual Image from Dataset" width="600"/>

### Results Summary
| `eps` Value | Object Clusters Detected | Valid Objects Compared with Original Image |
|:---:|:---:|:---:|
| 0.5 | 39 | 6 |
| 0.8 | 31 | 5 |
| 1.0 | 26 | 10 |


## Analysis of Results
From the visualizations, we can see that as the `eps` parameter increases, the number of detected clusters decreases, and the size of the clusters increases. This is because a larger `eps` value allows points that are farther apart to be considered part of the same cluster, resulting in fewer but larger clusters. Conversely, a smaller `eps` value results in more clusters that are smaller in size, as only points that are closer together are grouped into the same cluster. 

However, we can see that the bounding boxes for the clusters detected with `eps = 0.5` although they are more, they are smaller and less accurate in encapsulating valid objects in the scene. We can see that with an `eps` value of 0.5, there are many small clusters that may represent noise or parts of objects rather than whole objects. On the other hand, with `eps = 0.8` there are fewer clusters, but they are larger merged clusters. Like the cluster that contains the park car on the right hand side of the image. The car and its surrounding points are merged into one cluster, which results in a bounding box that is extremely larger than the actual car. With eps = 1.0 there are fewer clusters overall because fragmented object components are merged into complete objects. Despite the larger neighborhood radius, most nearby objects remain sufficiently separated, resulting in bounding boxes that more accurately represent real-world objects. The bounding boxes for the clusters detected with `eps = 1.0` are more accurate in encapsulating valid objects in the scene, as they are larger and more likely to encompass entire objects rather than just parts of them.


## Phase 6 Configuration
```text
ROI:
x = [0, 40]
y = [-20, 20]
z = [-2, 2]

Voxel Size: 0.2

RANSAC:
Distance Threshold: 0.2
Ransac N: 3
Num Iterations: 1000

DBSCAN:
eps: 1.0
min_samples: 15

Results:
26 clusters detected
10 valid objects
```

## Conclusion
The DBSCAN parameter `eps` significantly affects object dectection performaance. Smaller values produce fragmented clusters that correspond to partial objects, while intermediate values may incorrectly merge nearby objects. For the KiTTi frame used in the experiment, an `eps` value of 1.0 provided the most accurate bounding-box representation of visible scene objects, resulting in approximately 10 valid object clusters that corresponded well with the actual objects in the original image. This analysis highlights the importance of tuning the `eps` parameter to achieve optimal clustering results for object detection tasks in LiDAR point cloud data.

