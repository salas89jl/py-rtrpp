# Phase 7: Rule-Based Object Classification

## Introduction
In this phase, the goal is to classify the detected clusters. Up to now, the current pipeline has been able to detect where objects are located in the point cloud, but it has not been able to determine what type of objects they are. In this phase, we will implement a simple rule-based classification system that categorizes clusters based on their size and shape.

## How the Rule-Based Classification Works
Recall from previous phases that for each cluster, we have calculated the length, width, and height by:

```
length = max_x - min_x
width = max_y - min_y
height = max_z - min_z
``` 
Different objects tend to have different size characteristics. For example, a car might have a length of around 3-5 meters, a width of around 1.5-2 meters, and a height of around 1-1.5 meters. A pedestrian might have a length of around 0.5-1 meter, a width of around 0.5-1 meter, and a height of around 1.5-2 meters. A cyclist might have a length of around 1.5-2 meters, a width of around 0.5-1 meter, and a height of around 1.5-2 meters. Any cluster that does not fit into these categories can be classified as "unknown".

## Classification Rules
Based on the size characteristics of different objects, we can define the following classification rules:   
| Object Type | Length (m) | Width (m) | Height (m) |
|-------------|------------|-----------|------------|
| Car         | 3-6        | 1.5-3     | 1-3.0      |
| Pedestrian  | < 1.5       | < 1.5    | 1.5-2.5    |
| Cyclist     | 1.5-2       | 0.5-1    |  1.5-2     |
| Unknown     | Any other size characteristics |    

## Building the Classifier
Step 1: Implement a function that takes the length, width, and height of a cluster as input and returns the object type based on the classification rules defined above.
Step 2: Integrate this classification function into the existing pipeline so that after clusters are detected and their size characteristics are calculated, they are classified accordingly.
Step 3: Test the classifier on the existing dataset and analyze the results to see how well it performs in classifying different objects.

## Step 1: Implementing the Classification Function
Here is a simple implementation of the classification function in Python we will call it `classify_object_simple`:

```python
def classify_object_simple(length, width, height):

    # Car
    if (
        3.0 <= length <= 6.0 and
        1.5 <= width <= 3.0 and 
        1.0 <= height <= 3.0 
    ): 
        return "Car"
    elif (
        1.5 <= length <= 3.0 and
        3.0 <= width <= 6.0 and 
        1.0 < height <= 3.0
    ):  
        return "Car"
    
    # Pedestrian
    elif (
        length < 1.5 and 
        width < 1.5 and 
        1.2 <= height <= 2.5
    ):
        return "Pedestrian"
    
    # Cyclist  
    elif (
        1.5 <= length <= 2.0 and 
        0.5 <= width <= 1.0 and 
        1.0 <= height <= 2.5 
    ):
        return "Cyclist"
    elif (
        0.5 <= length <= 1.0 and
        1.5 <= width <= 2.0 and 
        1.0 <= height <= 2.5
    ):
        return "Cyclist"
    
    return "Unknown"
```
Note that the classification rules are not perfect and may need to be adjusted based on the specific dataset and the types of objects present. Additionally, this simple rule-based classifier may not perform well in all cases, especially when there is significant overlap in the size characteristics of different object types. In future phases, we can explore more advanced classification techniques, such as machine learning-based classifiers, to improve the accuracy of object classification.

## Step 2: Integrating the Classifier into the Pipeline
To integrate the `classify_object_simple` function into the existing pipeline, we will modify the part of the code where we calculate the size characteristics of each cluster box. After calculating the length, width, and height for each cluster, we will call the `classify_object_simple` function to determine the object type and store this information for later analysis and visualization.

```python
    # Compute the bounding box dimensions for analysis
    box = compute_bounding_box(cluster_points)

    # classify all of the object clusters based on box dimensions
    classified_objects = classify_object_simple(
        box["length"],
        box["width"],
        box["height"]
    )

    # Print clasification
    center = bbox.get_center()

    print(
        f"Cluster {cluster_id}: {label} | "
        f"Center=({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}) | "
        f"L={box['length']:.2f}, "
        f"W={box['width']:.2f}, "
        f"H={box['height']:.2f}"
    )
```
## Step 3: Testing the Classifier
After integrating the classifier into the pipeline and running it on the existing dataset, we can analyze the results to see how well it performs in classifying different objects.

### Results

<img src="/images/ph7_classification.png" alt="Classification Results" width="600"/>

```
Cluster 0: Car | Center=(5.82, 8.40, -0.72) | L=1.57, W=3.51, H=1.35
Cluster 1: Unknown | Center=(8.66, -14.12, -0.18) | L=17.30, W=11.73, H=2.17
Cluster 2: Unknown | Center=(8.61, -6.44, -0.35) | L=1.14, W=1.64, H=1.81
Cluster 4: Unknown | Center=(7.39, 17.12, -0.25) | L=14.71, W=5.73, H=2.40
Cluster 5: Pedestrian | Center=(11.37, 7.97, -0.35) | L=0.30, W=0.38, H=1.96
Cluster 6: Car | Center=(13.07, -5.75, -0.67) | L=1.56, W=3.74, H=1.16
Cluster 8: Unknown | Center=(11.91, 10.24, -1.38) | L=2.45, W=2.62, H=0.03
Cluster 9: Pedestrian | Center=(14.35, -1.54, -0.61) | L=1.16, W=0.58, H=1.31
Cluster 11: Pedestrian | Center=(16.36, 5.39, -0.60) | L=0.67, W=0.84, H=1.23
Cluster 12: Unknown | Center=(25.38, 7.32, -0.06) | L=5.15, W=4.23, H=2.47
Cluster 13: Cyclist | Center=(25.92, -13.44, 0.13) | L=0.55, W=1.52, H=2.13
Cluster 14: Unknown | Center=(34.92, 13.78, 0.11) | L=0.79, W=1.03, H=2.73
Cluster 15: Unknown | Center=(31.13, -6.02, -0.74) | L=0.39, W=2.76, H=0.56
Cluster 16: Unknown | Center=(34.68, 6.10, 0.14) | L=2.72, W=2.20, H=2.59
Cluster 17: Car | Center=(33.60, -15.13, 0.70) | L=4.16, W=2.68, H=1.59
Cluster 18: Pedestrian | Center=(37.58, -4.18, 0.24) | L=0.47, W=0.96, H=1.66
Cluster 19: Unknown | Center=(37.83, 16.49, 0.12) | L=3.57, W=6.20, H=2.50
Cluster 20: Unknown | Center=(27.02, 18.30, -0.00) | L=5.21, W=3.30, H=2.67
Cluster 21: Unknown | Center=(35.72, -18.97, 0.38) | L=2.76, W=2.05, H=2.46
Cluster 22: Unknown | Center=(18.26, -5.80, 0.33) | L=0.64, W=0.73, H=1.06
Cluster 23: Unknown | Center=(8.95, -10.29, 0.44) | L=1.16, W=1.27, H=0.51
Cluster 24: Unknown | Center=(24.68, -6.55, -0.05) | L=1.38, W=1.93, H=2.23
Cluster 26: Pedestrian | Center=(24.41, -3.31, -0.52) | L=0.38, W=0.51, H=1.37
Cluster 27: Pedestrian | Center=(37.30, -10.01, 0.45) | L=0.84, W=0.79, H=2.13
Cluster 29: Unknown | Center=(30.24, 13.60, 0.65) | L=1.16, W=2.59, H=1.41
Cluster 30: Pedestrian | Center=(33.49, 16.91, 0.82) | L=0.84, W=1.30, H=1.34
```
### Analysis of Results
<!-- Update table with new output -->
|Cluster ID| Classification| Visual Inspection|
|----------|----------------|-----------------|
|0| Car | Car |
|1| Unknown | Unknown |
|2| Unknown | Right side tree-like structure |
|4| Unknown | left side structure |
|5| Pedestrian | None Pedestrian |
|6| Car | Car |
|8| Unknown | Unknown |
|9| Pedestrian | Pedestrian |
|11| Pedestrian | Pedestrian |
|12| Unknown | Unknown |
|13| Cyclist | Unknown |
|14| Unknown | Unknown |
|15| Unknown | Unknown |
|16| Unknown | Unknown |
|17| Car | Unknown |
|18| Pedestrian | Unknown |
|19| Unknown | Unknown |
|20| Unknown | Unknown |
|21| Unknown | Unknown |
|22| Unknown | Unknown |
|23| Unknown | Unknown |
|24| Unknown | Unknown |
|26| Pedestrian | Pedestrian |
|27| Pedestrian | Unknown |
|29| Unknown | Unknown |
|30| Pedestrian | Unknown |

From the results, we can see that the simple rule-based classifier is able to correctly classify some of the clusters objects, such as cars, pedestrians, and cyclists. However, there are also many clusters that are classified as "unknown" or misclassified. This is likely due to the limitations of the simple rule-based approach. The limitations of the simple rule-based approach include:
- Overlapping size characteristics: Different object types may have overlapping size characteristics, making it difficult to accurately classify them based solely on size.
- Variability in object sizes: Objects of the same type may have different sizes, which can lead to misclassification if the classification rules are too rigid.
- Noise and outliers: The presence of noise and outliers in th point cloud data can affect the accuracy of the size calculations and, consequently, the classification results.

## Phase 7 Conclusion
The simple rule-based classification system was able to classify several obvious clusters correctly and pedestrians using the bounding-box dimensions. However, many of the clusters were classified as Unknown or misclassified becuase object size alone is not enough to relaibly identify objects in a LiDAR scene. Major limitations included overlapping object dimensions, variation in object size, point cloud noise, partial object scans, merged clusters, and distortion from axis-aligned bounding boxes. Overall, Phase 7 demonstrated the basic idea of feature-based classification, where bounding box measurements such as length, width, and height, and volume can be used to estimate the type of object. 