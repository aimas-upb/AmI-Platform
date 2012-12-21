import array
import os
import uuid

from PIL import Image
from pybetaface.api import BetaFaceAPI

from core import PDU

class UpgradeFaceSamples(PDU):
    QUEUE = 'upgrade_face_samples'
    
    def __init__(self, **kwargs):
        super(UpgradeFaceSamples, self).__init__()
        self.api = BetaFaceAPI()
    
    def save_image_to_file(self, buffer, width, height, path):
        image_buffer = array.array('B', buffer).tostring()
        image_to_file = Image.frombuffer("RGB", (width, height), 
                                 image_buffer)
        image_to_file.save(path)

    def process_message(self, message):
        # parse message
        person_name = message['person_name']
        image = message['image']
        width = int(message['width'])
        height = int(message['height'])
        
        # save image to file
        path = "/tmp/%s.jpg" % uuid.uuid4()

        self.save_image_to_file(image, width, height, path)
     
        # upload image to BetaFace API
        self.api.upload_face(path, person_name)

        os.remove(str(path))
        
if __name__ == "__main__":
    module = UpgradeFaceSamples()
    module.run()