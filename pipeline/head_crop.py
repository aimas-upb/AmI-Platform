import copy
import logging
import time

from core import ParallelPDU
from lib.image import base64_to_image, image_to_base64
from lib.kinect import crop_head_using_skeleton
from lib.logging import setup_logging
from lib.opencv import crop_face_from_image

logger = logging.getLogger(__name__)
MAX_TIME = 0.1


def _crop_head_using_skeleton(last_image, last_skeleton):
    """ Given the last image and last skeleton which are
        'close enough' apart, crop off an image of the head. """
    image = base64_to_image(last_image['image'],
                            int(last_image['width']),
                            int(last_image['height']))
    skeleton = last_skeleton

    return crop_head_using_skeleton(image, skeleton)


def _crop_head_using_face_detection(last_image):
    """ Given the last image, try to detect any faces in it
        and crop the first one of them, if any. """
    image = base64_to_image(last_image['image'],
                            int(last_image['width']),
                            int(last_image['height']))
    return crop_face_from_image(image)


def crop_head(message):
    last_image = message['hack']['last_image']
    last_image_at = message['hack']['last_image_at']
    last_skeleton = message['hack']['last_skeleton']
    last_skeleton_at = message['hack']['last_skeleton_at']

    cropped_head = None

    # If this is an image, and we have a "recent" skeleton, or vice-versa
    # try to crop the face. For this, we need to have
    # at least one skeleton and one image.
    if (last_image is not None and last_skeleton is not None and
        abs(last_image_at - last_skeleton_at) < MAX_TIME):
        cropped_head = _crop_head_using_skeleton(last_image, last_skeleton)

    # If we have no "recent" skeleton or no skeleton at all,
    # we'll detect the face from image
    elif (last_image is not None):
        cropped_head = _crop_head_using_face_detection(last_image)

    if cropped_head is not None:
        return image_to_base64(cropped_head)
    else:
        return None


class HeadCrop(ParallelPDU):
    """ PDU that receives images and skeletons from Router
        and crops images (head only) """

    QUEUE = 'head-crop'
    MAX_TIME = 0.1

    def __init__(self, **kwargs):
        kwargs['heavy_preprocess'] = crop_head
        super(HeadCrop, self).__init__(**kwargs)
        self.last_image = None
        self.last_image_at = None
        self.last_skeleton = None
        self.last_skeleton_at = None

    def process_message(self, message):
        # Step 1 - always update last_image/last_skeleton
        if message['type'] == 'image_rgb' and\
            message['sensor_type'] == 'kinect':
            self.last_image = message['image_rgb']
            self.last_image_at = time.time()
        elif message['type'] == 'skeleton' and\
            message['sensor_type'] == 'kinect':
            self.last_skeleton = message['skeleton_2D']
            self.last_skeleton_at = time.time()

        message['hack'] = {}
        message['hack']['last_image'] = copy.copy(self.last_image)
        message['hack']['last_image_at'] = self.last_image_at
        message['hack']['last_skeleton'] = copy.copy(self.last_skeleton)
        message['hack']['last_skeleton_at'] = self.last_skeleton_at

        super(HeadCrop, self).process_message(message)

    def light_postprocess(self, cropped_head, image_dict):
        # Route cropped images to face-recognition
        if cropped_head is not None:
            self.log("Sending an image to face recognition")
            self._send_to_recognition(cropped_head)

    def _send_to_recognition(self, image):
        """ Send a given image to face recognition. """
        self.send_to('face-recognition', {'head_image': image})

if __name__ == "__main__":
    setup_logging()
    module = HeadCrop()
    module.run()
