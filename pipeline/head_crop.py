import array
import base64
import math
import time
import uuid

from core import PDU
from PIL import Image

import cv

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
            cropped_head = self.crop_head()
            
        # If we have no "recent" skeleton or no skeleton at all,
        # we'll detect the face from image
        elif (self.last_image is not None):
            cropped_head = self.face_detect()
            
        # Route cropped images to face-recognition
        if cropped_head is not None:
            self.send_to('face-recognition', cropped_head)
        return
    
    def skeleton2d(self, key, subkey):
        """ Integer value of skeleton[key][subkey] """
        return int(self.last_skeleton['skeleton_2d'][key][subkey])
    
    def image(self, key):
        return int(self.last_image[key])
        
    def dist(self, x1, y1, x2, y2):
        """ Integer distance between two points. """
        return int( math.sqrt( 
                    (x1-x2)*(x1-x2) + 
                    (y1-y2)*(y1-y2) ))

    def skeleton2d_radius(self):
        pts = [self.skeleton2d(key, subkey)\
               for key in ['head', 'neck']
               for subkey in ['X', 'Y']]
        return self.dist(*pts)
     
    def skeleton2d_cropping_area(self):
        center_x = (self.skeleton2d('head', 'X') + self.skeleton2d('neck', 'X')) / 2
        center_y = (self.skeleton2d('head', 'Y') + self.skeleton2d('neck', 'Y')) / 2
        radius = self.skeleton2d_radius()
        min_x = max(center_x - radius, 0)
        min_y = max(center_y - radius, 0)
        max_x = min(center_x + radius, self.image('width'))
        max_y = min(center_y + radius, self.image('height'))
        return [min_x, min_y, max_x, max_y]
    
    def crop_image(self, image, min_x, min_y, max_x, max_y):
        cropped_image = []
        width = self.image('width')
        
        for y in range(max_y, min_y, -1):
            for x in range(max_x, min_x, -1):
                idx = (y * width + x) * 3
                cropped_image.append (image[ idx ])
                cropped_image.append (image[ idx + 1 ])
                cropped_image.append (image[ idx + 2 ])
        
        return {'image': cropped_image, 'width': max_x-min_x, 'height': max_y-min_y}

    def crop_head(self):
        decoded_image = bytearray(base64.b64decode(self.last_image['image']))
        [min_x, min_y, max_x, max_y] = self.skeleton2d_cropping_area()
          
        return self.crop_image(decoded_image, min_x, min_y, max_x, max_y) 

    def face_detect(self):
        received_image = self.last_image['image']
        width = self.last_image['width']
        height = self.last_image['height']
        
        # temporary save image to disk
        image_buffer = array.array('B', received_image).tostring()
        image = Image.frombuffer("RGB", (width, height), image_buffer)
        
        path = "/tmp/face_detection_%s.jpg" % uuid.uuid4()
        image.save(path)
        
        hc = cv.Load('/home/ami/AmI-Platform/resources/haarcascade_frontalface_default.xml')
        img = cv.LoadImage(path, cv.CV_LOAD_IMAGE_COLOR)
        faces = cv.HaarDetectObjects(img, hc, cv.CreateMemStorage(), 1.2, 2,cv.CV_HAAR_DO_CANNY_PRUNING, (100,100))

        # if multiple faces detected, send only the first one
        if len(faces) > 0:
            (x,y,w,h),n = faces[0]
            decoded_image = bytearray(base64.b64decode(received_image))
            x1 = max(x - w/2, 0)
            y1 = max(y - h/2, 0)
            x2 = min(x + w * 3 / 2, width)
            y2 = min(y + h * 3 / 2, height)
            return self.crop_image(decoded_image, x1, y1, x2, y2)
            
        #os.remove(str(path))
        return None
        
if __name__ == "__main__":
    module = HeadCrop()
    module.run()
