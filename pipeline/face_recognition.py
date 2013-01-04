import array
import uuid

from PIL import Image

from pybetaface.api import BetaFaceAPI
from core import ParallelPDU

def betaface_recognition(image_dict):
    """ Given a message contained a cropped head, send it to BetaFace
        API for face recognition. This can take anywhere from 1 to 10 seconds.
    """
    api = BetaFaceAPI()
    image_buffer = array.array('B', image_dict['image']).tostring()
    image = Image.frombuffer("RGB",
                             (image_dict['width'], image_dict['height']),
                             image_buffer)

    # create the output file
    path = "/tmp/%s.jpg" % uuid.uuid4()
    print("Saving cropped face to %s" % path)
    image.save(path)

    matches = api.recognize_faces(path, 'amilab.ro')
    #os.remove(str(path))
    return matches

class FaceRecognition(ParallelPDU):
    """ PDU that receives cropped images (head only)
    and saves them to file """

    QUEUE = 'face-recognition'
    ORDERED_DELIVERY = True
    POOL_SIZE = 8

    def light_postprocess(self, matches, image_dict):
        self.log("Received matches from BetaFace: %r" % matches)

        # No persons means we're out of here.
        if len(matches) == 0:
            return

        # No strong bias towards a given person also gets us out of here.
        max_probability = max(matches.values())
        if max_probability < 0.75:
            return

        # Get the person with the maximal probability from BetaFace
        person_name = matches.keys()[matches.values().index(max_probability)]
        self.log("MOST_PROBABLE_PERSON = %s" % person_name)

        # Send event to room. This will cause interactivity within the lab.
        message_to_room = {'event_type': 'person_appeared',
                           'person_name': person_name}
        self.send_to('room', message_to_room)

        # send cropped image to UpgradeFaceSamples
        upgrade_message = {'person_name': person_name}
        upgrade_message.update(image_dict)
        self.send_to('upgrade_face_samples', upgrade_message)

if __name__ == "__main__":
    module = FaceRecognition(heavy_preprocess = betaface_recognition)
    module.run()
