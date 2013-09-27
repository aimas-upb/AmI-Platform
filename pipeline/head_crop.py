import copy
import logging
import time

from core import ParallelPDU
from lib.image import base64_to_image, image_to_base64
from lib.kinect import crop_head_using_skeleton
from lib.log import setup_logging
from lib.opencv import crop_face_from_image
from lib.session_tracker import SessionTracker

logger = logging.getLogger(__name__)
MAX_TIME = 5000 # milliseconds


def _crop_head_using_skeleton(last_image, last_skeleton):
    """ Given the last image and last skeleton which are
        'close enough' apart, crop off an image of the head. """
    image = base64_to_image(last_image['image'],
                            int(last_image['width']),
                            int(last_image['height']),
                            last_image['encoder_name'])
    skeleton = last_skeleton

    return crop_head_using_skeleton(image, skeleton)


def _crop_head_using_face_detection(last_image):
    """ Given the last image, try to detect any faces in it
        and crop the first one of them, if any. """
    image = base64_to_image(last_image['image'],
                            int(last_image['width']),
                            int(last_image['height']),
                            last_image['encoder_name'])
    return crop_face_from_image(image)


def crop_head(message):
    last_image = message['hack']['last_image']
    last_image_at = message['hack']['last_image_at']
    last_skeleton = message['hack']['last_skeleton']
    last_skeleton_at = message['hack']['last_skeleton_at']

    # No image means nothing to crop, se we're done.
    if last_image is None:
        return None

    cropped_head = None

    # If this is an image, and we have a "recent" skeleton, or vice-versa
    # try to crop the face. For this, we need to have
    # at least one skeleton and one image.
    if last_skeleton is not None:
        if abs(last_image_at - last_skeleton_at) < MAX_TIME/1000:
            logger.info("Trying to crop head using correlation between "
                        "skeleton and RGB image: %r secs." %
                        (abs(last_skeleton_at - last_image_at) / 1000))
            cropped_head = _crop_head_using_skeleton(last_image, last_skeleton)
        else:
            logger.info("Cannot crop head using correlation between skeleton "
                        "and image because they are too far apart: %r secs." %
                        (abs(last_skeleton_at - last_image_at) / 1000))
            cropped_head = _crop_head_using_face_detection(last_image)

    if cropped_head:
        return image_to_base64(cropped_head)


class HeadCrop(ParallelPDU):
    """ PDU that receives images and skeletons from Router
        and crops images (head only) """

    QUEUE = 'head-crop'
    POOL_SIZE = 20
    UNFINISHED_TASKS_THRESHOLD = 2 * POOL_SIZE

    def __init__(self, **kwargs):
        kwargs['heavy_preprocess'] = crop_head
        super(HeadCrop, self).__init__(**kwargs)
        self.last_image = {}
        self.last_image_at = {}
        self.last_skeleton = {}
        self.last_skeleton_at = {}
        self.session_tracker = SessionTracker()

    def process_message(self, message):
        # Step 1 - always update last_image/last_skeleton
        sensor_id = message['sensor_id']
        if (message['type'] == 'image_rgb' and
            message['sensor_type'] == 'kinect'):
                self.last_image[sensor_id] = message['image_rgb']
                if not 'encoder_name' in self.last_image[sensor_id]:
                    self.last_image[sensor_id]['encoder_name'] = 'raw'
                self.last_image_at[sensor_id] = message['created_at']

        elif message['type'] == 'skeleton' and\
            message['sensor_type'] == 'kinect':
            self.last_skeleton[sensor_id] = message['skeleton_2D']
            self.last_skeleton_at[sensor_id] = message['created_at']

        message['hack'] = {}
        message['hack']['last_image'] = copy.deepcopy(self.last_image.get(sensor_id))
        message['hack']['last_image_at'] = self.last_image_at.get(sensor_id)
        message['hack']['last_skeleton'] = copy.deepcopy(self.last_skeleton.get(sensor_id))
        message['hack']['last_skeleton_at'] = self.last_skeleton_at.get(sensor_id)

        super(HeadCrop, self).process_message(message)

    def light_postprocess(self, cropped_head, image_dict):
        # Route cropped images to face-recognition
        if cropped_head is not None:
            self.log("Sending an image to face recognition")
            self._send_to_recognition(cropped_head)
            self.session_tracker.track_event(image_dict['session_id'],
                                             image_dict['created_at'],
                                             {"head": cropped_head})

    def _send_to_recognition(self, image):
        """ Send a given image to face recognition. """
        self.send_to('face-recognition', {'head_image': image})

if __name__ == "__main__":
    setup_logging()
    module = HeadCrop()
    module.run()
