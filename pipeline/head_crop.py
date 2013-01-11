import time

from core import PDU
from lib.image import base64_to_image, image_to_base64
from lib.kinect import crop_head_using_skeleton
from lib.opencv import crop_face_from_image

class HeadCrop(PDU):
    """ PDU that receives images and skeletons from Router 
        and crops images (head only) """

    QUEUE = 'head-crop'
    MAX_TIME = 0.1
    
    def __init__(self):
        super(HeadCrop, self).__init__()
        self.last_image = None
        self.last_skeleton = None
        
    def process_message(self, message):
        # Step 1 - always update last_image/last_skeleton
        if message['sensor_type'] == 'kinect_rgb':
            self.last_image = message
            self.last_image_at = time.time()
        elif message['sensor_type'] == 'kinect':
            self.last_skeleton = message
            self.last_skeleton_at = time.time()
        
        cropped_head = None
        
        # If this is an image, and we have a "recent" skeleton, or vice-versa
        # try to crop the face. For this, we need to have
        # at least one skeleton and one image.
        if (self.last_image is not None and self.last_skeleton is not None and
            abs(self.last_image_at - self.last_skeleton_at) < self.MAX_TIME):
            cropped_head = self._crop_head_using_skeleton()
            
        # If we have no "recent" skeleton or no skeleton at all,
        # we'll detect the face from image
        elif (self.last_image is not None):
            cropped_head = self._crop_head_using_face_detection()
            
        # Route cropped images to face-recognition
        if cropped_head is not None:
            self._send_to_recognition(cropped_head)
    
    def _crop_head_using_skeleton(self):
        """ Given the last image and last skeleton which are 
            'close enough' apart, crop off an image of the head. """
        image = base64_to_image(self.last_image['image'],
                                int(self.last_image['width']),
                                int(self.last_image['height']))
        skeleton = self.last_skeleton['skeleton_2d']
        
        return crop_head_using_skeleton(image, skeleton)

    def _crop_head_using_face_detection(self):
        """ Given the last image, try to detect any faces in it
            and crop the first one of them, if any. """
        image = base64_to_image(self.last_image['image'],
                                int(self.last_image['width']),
                                int(self.last_image['height']))
        return crop_face_from_image(image)
    
    def _send_to_recognition(self, image):
        """ Send a given image to face recognition. """
        self.send_to('face-recognition', image_to_base64(image))
        
if __name__ == "__main__":
    module = HeadCrop()
    module.run()
