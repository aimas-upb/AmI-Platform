from geometry import dist, rectangle_intersection

def crop_head_using_skeleton(image, skeleton):
    """ Given an image taken from the kinect RGB in PIL format, and a set
        of skeleton coordinates, crop the head and return the cropped image.
    """

    # We will cut off a rectangle with the center in the head
    # and the dimension 2 * head-neck distance.
    neck_length = dist(skeleton['head']['X'], skeleton['head']['Y'],
                       skeleton['neck']['X'], skeleton['neck']['Y'])
    head_rect = (skeleton['head']['X'] - neck_length,
                 skeleton['head']['Y'] - neck_length,
                 skeleton['head']['X'] + neck_length,
                 skeleton['head']['Y'] + neck_length)

    # Intersect our rectangle with the actual image, and crop it
    image_rect = (0, 0, image.size[0], image.size[1])
    cropping_rect = rectangle_intersection(head_rect, image_rect)
    cropping_rect = (int(cropping_rect[0]), int(cropping_rect[1]),
                     int(cropping_rect[2]), int(cropping_rect[3]))

    return image.crop(cropping_rect)
