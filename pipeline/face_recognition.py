import logging
import os

from core import ParallelPDU
from core.constants import (SKYBIOMETRY_NAMESPACE, SKYBIOMETRY_API_KEY,
                            SKYBIOMETRY_API_SECRET)
from lib.log import setup_logging
from lib.s3 import save_image, upload_to_s3
from lib.session_tracker import SessionTracker
from pybetaface.api import BetaFaceAPI
from sky_biometrics.face_client import FaceClient

logger = logging.getLogger(__name__)


def betaface_recognition(image_dict):
    """ Given a message contained a cropped head, send it to BetaFace
        API for face recognition. This can take anywhere from 1 to 10 seconds.
    """
    try:
        api = BetaFaceAPI()

        image_path = save_image(image_dict['head_image']['image'],
                                int(image_dict['head_image']['width']),
                                int(image_dict['head_image']['height']),
                                prefix="FR_")

        matches = api.recognize_faces(image_path, 'amilab.ro')
        logger.info("Received recognized faces from BetaFace API %r" % matches)

        # os.remove(str(temp_path))
        # logger.info("Removed image from disk (%s)" % str(temp_path))

        return matches
    except:
        logger.exception("Failed to recognize faces via BetaFace API")
        return {}


def skybiometry_recognition(image_dict):
    """ Given a message contained a cropped head, send it to SkyBiometry
        API for face recognition. This can take anywhere from X to Y seconds.
    """
    try:
        api = FaceClient(SKYBIOMETRY_API_KEY, SKYBIOMETRY_API_SECRET)

        local_path = save_image(image_dict['head_image']['image'],
                                int(image_dict['head_image']['width']),
                                int(image_dict['head_image']['height']),
                                prefix="FR_")
        image_url = upload_to_s3(local_path)

        response = api.faces_recognize('all', image_url,
                                       namespace=SKYBIOMETRY_NAMESPACE)

        # os.remove(str(image_path))
        # logger.info("Removed image from disk (%s)" % str(temp_path))

        logger.debug("Response from SkyBiometry: %r" % response)
        tags = response['photos'][0]['tags']
        if tags:
            matches = tags[0]['uids']
            logger.info("Received recognized faces from SkyBiometry API %r" %
                        matches)
            return to_dict(matches)
        else:
            return {}

    except:
        logger.exception("Failed to recognize faces via SkyBiometry API")
        return {}


def to_dict(matches):
    """Transforms SkyBiometry matches format to dictionary.

    Example:
        from:
            [{u'confidence': 70, u'uid': u'diana@amilab-test2'},
            {u'confidence': 52, u'uid': u'andrei@amilab-test2'}]
        to:
            {u'diana@amilab-test2': 70,
             u'andrei@amilab-test2': 52}
    """
    result = {}

    for match in matches:
        result.update({match['uid']: match['confidence']})

    return result


class FaceRecognition(ParallelPDU):
    """ PDU that receives cropped images (head only)
    and saves them to file """

    QUEUE = 'face-recognition'
    ORDERED_DELIVERY = True
    POOL_SIZE = 8
    UNFINISHED_TASKS_THRESHOLD = 2 * POOL_SIZE
    BEST_PERSON_THRESHOLD = 0.75
    UPGRADE_FACE_SAMPLES_THRESHOLD = 0.85

    def __init__(self, **kwargs):
        # kwargs['heavy_preprocess'] = betaface_recognition
        kwargs['heavy_preprocess'] = skybiometry_recognition
        super(FaceRecognition, self).__init__(**kwargs)
        self.session_tracker = SessionTracker()

    def process_message(self, message):
        image_rgb = message['head_image']
        save_image(image_rgb['image'], image_rgb['width'], image_rgb['height'], "TO_FR_FR_")
        super(FaceRecognition, self).process_message(message)

    def light_postprocess(self, matches, image_dict):
        self.logger.info("Received matches from FaceRecognition: %r" % matches)

        # No persons means we're out of here.
        if len(matches) == 0:
            self.logger.info("Bailing out because of empty matches from "
                             "FaceRecognition")
            return

        # No strong bias towards a given person also gets us out of here.
        max_probability = max(matches.values())
        if max_probability < self.BEST_PERSON_THRESHOLD:
            self.logger.info("Out of the matches returned by FaceRecognition, "
                             "the maximum confidence is only %.2f "
                             "(should have been at least %.2f)"\
                             % (max_probability, self.BEST_PERSON_THRESHOLD))
            return

        # Get the person with the maximal probability from FaceRecognition
        person_name = matches.keys()[matches.values().index(max_probability)]
        self.logger.info("MOST_PROBABLE_PERSON = %s" % person_name)

        # Send event to room. This will cause interactivity within the lab.
        message_to_room = {'event_type': 'person_appeared',
                           'person_name': person_name}
        self.send_to('room', message_to_room)
        if 'session_id' in image_dict.keys():
            self.session_tracker.track_event(image_dict['session_id'],
                                             0, # set the person name globally on the session
                                             {'person_name': person_name})

        # Send cropped image to UpgradeFaceSamples only if detection confidence
        # is really really high. Otherwise it's not worth it and we will
        # pollute the data structures in FaceRecognition API.
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
