from faces import face_detect
from geometry import rectangle_scale, rectangle_intersection

def crop_face_from_image(image):
    """ Return a cropped face from a given image. """
    
    # Try to detect faces in the image - if there is None,
    # there is nothing to do. Otherwise, keep only the first
    # face regardless of how many were detected. 
    faces = face_detect(image)
    if len(faces) == 0:
        return None
    
    (x, y, w, h) = faces[0][0]
    
    # Take the first detected face and scale the rectangle
    # 2 times around its center.
    face_rect = (x, y, x + w, y + h)
    face_rect = rectangle_scale(*face_rect, factor = 2)
    
    # Intersect this with the image rectangle
    image_rect = (0, 0, image.size[0], image.size[1])
    cropping_rect = rectangle_intersection(face_rect, image_rect)
    
    return image.crop(cropping_rect)