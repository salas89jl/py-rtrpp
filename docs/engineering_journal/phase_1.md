# Phase 1 Learn Basics of Point Cloud Data
In this phase, the goal is to set up the environment by seperating the project into clean parts: 
```text
generate data --> transform coordinates --> visualize the results
```
This will allows us to focus on each part separately and make sure that each part is working correctly before moving on to the next part. 

## What is a Point Cloud?
A point cloud is massive collection of raw data points plotted in a 3D coordinate system (x, y, z). It represents the exact external surface of a physical object, landscape, or interior space, functioning as the movst basic form of a digital 3D model. Additionaly, point clouds can also include attributes such as color, intensity, and normal vectors, which provide more information about the surface properties of the objects being represented. 

## Generate Data

To generate data, we can use a simple mathematical model to create a point cloud that represents a circle. The equation of a circle in Cartesian coordinates is given by:

```text
x = r * cos(theta)
y = r * sin(theta)
```

Where `r` is the radius of the circle and `theta` is the angle that varies from 0 to 2*pi. By varying `theta`, we can generate points that lie on the circumference of the circle. 

We can use a loop to iterate through values of `theta` and calculate the corresponding `x` and `y` coordinates to create a point cloud.

To keep things separate, we can create a file name coordinates.py that contains the code for generating the point cloud data. This file will be reponsible for generating the data and can be imported into other parts of the project as needed.

__coordinates.py__
```python
import numpy as np

def polar_to_caresian(r, theta):
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y
```

Next we can create a file named synthetic_scan.py that will use the coordinates.py file to generate a point cloud for a circle. This file will be responsible for creating the synthetic scan data that we will use for testing and visualization.

```python
import numpy as np

def generate_circle_scan(r, num_points):
    theta = np.linspace(0, 2 * np.pi, num_points)
    x, y = polar_to_caresian(r, theta)
    return x, y
```

Next we can create a file named visualize.py that will be responsible for visualizing the point cloud data. This file will use a library such as Matplotlib to create a scatter plot of the points in the point cloud.

```python
import matplotlib.pyplot as plt
def plot_2d_points(x, y, title):
    plt.scatter(x, y, s=5)
    plt.axis("equal")
    plt.title(title)
    plt.xlabel("x position")
    plt.ylabel("y position")
    plt.show()
```

Finally, we can create a run_phase1.py file that will tie everything together. This file will import the necessary functions from the other files and execute the code to generate the point cloud data and visualize it.

```python
from coordinates import polar_to_caresian
from synthetic_scan import generate_circle_scan
from visualize import plot_2d_points

if __name__ == "__main__":
    r = 5  # radius of the circle
    num_points = 100  # number of points in the point cloud
    x, y = generate_circle_scan(r, num_points)
    plot_2d_points(x, y, "2D LiDar Scan")
```




Questions to answer:

* Why does this produce a circle? 
The equation of a circle in Cartesian coordinates is given by x = r * cos(theta) and y = r * sin(theta). By varying theta from 0 to 2*pi, we can generate points that lie on the circumference of the circle. The radius r determines how far the points are from the origin, and the angle theta determines their position around the circle.
* What happens if r varies?
If r varies, the points will no longer lie on the circumference of a circle. Instead, they will form a spiral pattern as the radius changes with each point. The points will be farther from the origin for larger values of r and closer to the origin for smaller values of r.
* What happens if noise is added? 
If noise is added to the point cloud data, the points will no longer lie perferctly on the circumference of the circle. Instead, they will be scattered around the circle, creating a more realistic representation of real-world LiDAR data, which often contains noise due to various factors such as sensor inaccuracies and environmental conditions. The points may appear more dispersed and less uniform, making it more challenging to identify the underlying shape of the circle. 