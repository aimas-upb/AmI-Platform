import math

def dist(x1, y1, x2, y2):
    """ Integer distance between two points. """

    return int( math.sqrt(
                (x1-x2)*(x1-x2) +
                (y1-y2)*(y1-y2) ))

def segment_intersection((x1, x2), (y1, y2)):
    """ Intersects two segments (x1, x2) and (y1, y2) """

    if y2 < x1 or x1 > y2:
        return None
    return (max(x1, y1), min(x2, y2))

def rectangle_intersection((r1x1, r1y1, r1x2, r1y2),
                           (r2x1, r2y1, r2x2, r2y2)):
    """ Intersect two rectangles given their lower left and upper right corners.

    Rectangles are given as quadruples in the following format:
    (x_lower_left, y_lower_left, x_upper_right, y_upper_right)

    Returns None if the rectangle do not intersect. Otherwise, it returns
    a quadruple in the same format as the input.

    """

    # Check if the rectangles intersect vertically
    vertical_intersection = segment_intersection((r1y1, r1y2), (r2y1, r2y2))
    horizontal_intersection = segment_intersection((r1x1, r1x2), (r2x1, r2x2))
    if vertical_intersection is None or horizontal_intersection is None:
        return None

    return ((horizontal_intersection[0], vertical_intersection[0],
             horizontal_intersection[1], vertical_intersection[1]))

def rectangle_center(x1, y1, x2, y2):
    """ Compute the center of a given rectangle. """
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def rectangle_scale(x1, y1, x2, y2, factor):
    """ Scale a rectangle with respect to its center, by a given factor.

    Coordinates are assumed to be integer, and in the standard rectangle format
    (see rectangle_intersection for more info).

    """
    (cx, cy) = rectangle_center(x1, y1, x2, y2)
    dx = cx - x1
    dy = cy - y1
    return (cx - factor * dx, cy - factor * dy,
            cx + factor * dx, cy + factor * dy)
