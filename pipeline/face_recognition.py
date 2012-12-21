import array
import os
import uuid

from PIL import Image

from pybetaface.api import BetaFaceAPI
from core import PDU

class FaceRecognition(PDU):
    """ PDU that receives cropped images (head only)
    and saves them to file """

    QUEUE = 'face-recognition'
    
    def __init__(self, **kwargs):
        super(FaceRecognition, self).__init__(**kwargs)
        self.api = BetaFaceAPI()
    
    def process_message(self, message):
        self.log("Processing a message")
        self.print_image_to_file(message)
        
    def print_image_to_file(self, image_dict):
        image_buffer = array.array('B', image_dict['image']).tostring()
        image = Image.frombuffer("RGB", 
                                 (image_dict['width'], image_dict['height']), 
                                 image_buffer)
        
        # create the output file
        path = "/tmp/%s.jpg" % uuid.uuid4()
        image.save(path)
        
        print "File path = %s" % path
        matches = self.api.recognize_faces(path, 'amilab.ro')
        print matches
        
        # get the most probable person
        if len(matches) == 0:
            return
        
        max_probability = max(matches.values())
        if max_probability < 0.75:
            return
        
        person_name = matches.keys()[matches.values().index(max_probability)]
        self.log("PERSON = %s" % person_name)
        
        # send event to room
        message_to_room = {'event_type': 'person_appeared', 'person_name': person_name}
        self.send_to('room', message_to_room)
        
        # send cropped image to UpgradeFaceSamples
        upgrade_message = {'person_name': person_name}
        upgrade_message.update(image_dict)
        self.send_to('upgrade_face_samples', upgrade_message)
        
        #os.remove(str(path))
        
if __name__ == "__main__":
    module = FaceRecognition()
    module.run()
