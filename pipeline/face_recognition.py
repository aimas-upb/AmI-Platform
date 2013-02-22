import logging
import os

from pybetaface.api import BetaFaceAPI
from core import ParallelPDU
from lib.image import base64_to_image
from lib.files import random_file_name
from lib.log import setup_logging

logger = logging.getLogger(__name__)


def betaface_recognition(image_dict):
    """ Given a message contained a cropped head, send it to BetaFace
        API for face recognition. This can take anywhere from 1 to 10 seconds.
    """
    try:
        api = BetaFaceAPI()

        # Get image from message, save it to disk and
        # pass it on to BetaFace API
        image = base64_to_image(image_dict['head_image']['image'],
                                int(image_dict['head_image']['width']),
                                int(image_dict['head_image']['height']))
        temp_path = random_file_name('jpg')
        logger.info("Generated random path to save image: %s" % temp_path)

        image.save(temp_path)
        logger.info("Saved image to disk at path %s" % temp_path)

        matches = api.recognize_faces(temp_path, 'amilab.ro')
        logger.info("Received recognized faces from BetaFace API %r" % matches)

        #os.remove(str(temp_path))
        #logger.info("Removed image from disk (%s)" % str(temp_path))

        return matches
    except:
        logger.exception("Failed to recognize faces via BetaFace API")
        return {}


class FaceRecognition(ParallelPDU):
    """ PDU that receives cropped images (head only)
    and saves them to file """

    QUEUE = 'face-recognition'
    ORDERED_DELIVERY = True
    POOL_SIZE = 8
    BEST_PERSON_THRESHOLD = 0.75
    UPGRADE_FACE_SAMPLES_THRESHOLD = 0.85

    def __init__(self, **kwargs):
        kwargs['heavy_preprocess'] = betaface_recognition
        super(FaceRecognition, self).__init__(**kwargs)

    def light_postprocess(self, matches, image_dict):
        self.logger.info("Received matches from BetaFace: %r" % matches)

        # No persons means we're out of here.
        if len(matches) == 0:
            self.logger.info("Bailing out because of empty matches from "
                             "BetaFace")
            return

        # No strong bias towards a given person also gets us out of here.
        max_probability = max(matches.values())
        if max_probability < self.BEST_PERSON_THRESHOLD:
            self.logger.info("Out of the matches returned by BetaFace, the "
                             "maximum confidence is only %.2f "
                             "(should have been at least %.2f)"\
                             % (max_probability, self.BEST_PERSON_THRESHOLD))
            return

        # Get the person with the maximal probability from BetaFace
        person_name = matches.keys()[matches.values().index(max_probability)]
        self.logger.info("MOST_PROBABLE_PERSON = %s" % person_name)

        # Send event to room. This will cause interactivity within the lab.
        message_to_room = {'event_type': 'person_appeared',
                           'person_name': person_name}
        self.send_to('room', message_to_room)

        # Send cropped image to UpgradeFaceSamples only if detection confidence
        # is really really high. Otherwise it's not worth it and we will
        # pollute the data structures in BetaFace API.
        if max_probability >= self.UPGRADE_FACE_SAMPLES_THRESHOLD:
            upgrade_message = {'person_name': person_name}
            upgrade_message.update(image_dict)
            self.send_to('upgrade-face-samples', upgrade_message)
        else:
            self.logger.info("It isn't worth it to send a face sample because "
                             "maximal confidence was only %.2f (should have "
                             "been at least %.2f" %\
                             (max_probability,
                              self.UPGRADE_FACE_SAMPLES_THRESHOLD))

if __name__ == "__main__":
    setup_logging()
    module = FaceRecognition()
    module.run()
