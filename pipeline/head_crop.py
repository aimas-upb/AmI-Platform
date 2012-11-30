import base64
import math
import time

from core import PDU

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
            
        # Step 2 - if this is an image, and we have a "recent" skeleton,
        # try to crop the face or vice-versa. For this, we need to have
        # at least one skeleton and one image.
        if self.last_image is None or self.last_skeleton is None:
            print "Don't have both image and skeleton"
            return
        
        # If they aren't "close enough in time", still do nothing
        if abs(self.last_image_at - self.last_skeleton_at) >= self.MAX_TIME:
            return
            
        cropped_head = self.crop_head()
        # Route cropped images to face-recognition
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
        
    def crop_head(self):
        decoded_image = bytearray(base64.b64decode(self.last_image['image']))  
        cropped_image = []

        [min_x, min_y, max_x, max_y] = self.skeleton2d_cropping_area()
        width = self.image('width')
        
        for y in range(max_y, min_y, -1):
            for x in range(max_x, min_x, -1):
                idx = (y * width + x) * 3
                cropped_image.append (decoded_image[ idx ])
                cropped_image.append (decoded_image[ idx + 1 ])
                cropped_image.append (decoded_image[ idx + 2 ])
        
        return {'cropped_image': cropped_image, 'width': max_x-min_x, 'height': max_y-min_y}
        
if __name__ == "__main__":
    module = HeadCrop()
    module.run()
