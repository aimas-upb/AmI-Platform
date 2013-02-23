import logging
import math

from faces import face_detect
from geometry import rectangle_scale, rectangle_intersection

logger = logging.getLogger(__name__)

def crop_face_from_image(image):
    """ Return a cropped face from a given image. """

    # Try to detect faces in the image - if there is None,
    # there is nothing to do. Otherwise, keep only the first
    # face regardless of how many were detected.
    faces = face_detect(image)
    if len(faces) == 0:
        return None

    (x, y, w, h) = faces[0][0]
    logger.info("Found face with width = %d pixels and height = %d pixels" % (w, h))

    # Take the first detected face and scale the rectangle
    # 2 times around its center.
    face_rect = (x, y, x + w, y + h)
    face_rect = rectangle_scale(*face_rect, factor = 2)
    logger.info("Doubling both dimensions to %d x %d" % (face_rect[2] - face_rect[0],
                                                         face_rect[3] - face_rect[1]))

    # Intersect this with the image rectangle
    image_rect = (0, 0, image.size[0], image.size[1])
    cropping_rect = rectangle_intersection(face_rect, image_rect)
    logger.info("Final cropping rect has dimensions %d x %d" % (cropping_rect[2] - cropping_rect[0],
                                                                cropping_rect[3] - cropping_rect[1]))

    return image.crop(cropping_rect)
