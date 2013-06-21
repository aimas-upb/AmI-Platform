from random import choice
import time

from factory import Factory
from core.constants import IMAGE_WIDTH, IMAGE_HEIGHT, SENSOR_IDS, SENSOR_TYPES
from factories import utils


def FaceRecognitionFactory():
    """ Generates a 'upgrade-face-samples' message which will be processed by
    UpgradeFaceSamples PDU.

    Example:
    {
    'head_image': {
                   'image': 'AAAAA',
                   'width':640,
                   'height': 480,
                   },
    'session_id': 'daq-04_1_0123456789ABCDEF',
    'created_at': 1366974699,
    }
    """
    user_id = 1
    sensor_type = choice(SENSOR_TYPES)
    session_id = "{sensor_id}_{user_id}_{hash}".format(sensor_id=choice(SENSOR_IDS[sensor_type]),
                                                       user_id=user_id,
                                                       hash=utils.get_random_hash(16))

    return {'head_image': {
                           'image': utils.get_random_image(IMAGE_WIDTH / 10,
                                                           IMAGE_HEIGHT / 10),
                           'width': IMAGE_WIDTH / 10,
                           'height': IMAGE_HEIGHT / 10},
            'session_id': session_id,
            'created_at': int(time.time())}
