import numpy as np


def calculate_angle(first_point, middle_point, end_point):
    """
    Calculates the angle between 3 points.
    Points should be lists or tuples: [x, y]
    """
    first = np.array(first_point)
    mid = np.array(middle_point)
    end = np.array(end_point)

    # Calculate radians and convert to degrees
    radians = np.arctan2(end[1] - mid[1], end[0] - mid[0]) - \
              np.arctan2(first[1] - mid[1], first[0] - mid[0])
    angle = np.abs(radians * 180.0 / np.pi)

    # Ensure angle is within 180 degrees
    if angle > 180.0:
        angle = 360 - angle

    return angle