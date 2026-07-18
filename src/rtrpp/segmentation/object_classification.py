def simple_classification(length, width, height):
    """
    Classify an object based on its bounding box dimensions (length, width, height).

    Parameters:
        length (float): The length of the bounding box.
        width (float): The width of the bounding box.
        height (float): The height of the bounding box.
    Returns:
        str: The classification label for the object ("Car", "Pedestrian", "Cyclist", or "Unknown").
    """
    # Car
    if 3.0 <= length <= 6.0 and 1.5 <= width <= 3.0 and 1.0 <= height <= 3.0:
        return "Car"
    elif 1.5 <= length <= 3.0 and 3.0 <= width <= 6.0 and 1.0 < height <= 3.0:
        return "Car"

    # Pedestrian
    elif length < 1.5 and width < 1.5 and 1.2 <= height <= 2.5:
        return "Pedestrian"

    # Cyclist
    elif 1.5 <= length <= 2.0 and 0.5 <= width <= 1.0 and 1.0 <= height <= 2.5:
        return "Cyclist"
    elif 0.5 <= length <= 1.0 and 1.5 <= width <= 2.0 and 1.0 <= height <= 2.5:
        return "Cyclist"

    return "Unknown"
