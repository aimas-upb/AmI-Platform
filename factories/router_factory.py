from factory import Factory
from random import choice
import time

from core.constants import SENSOR_IDS, SENSOR_TYPES, IMAGE_WIDTH, IMAGE_HEIGHT
from factories import utils


def RouterFactory(message_type):
    sensor_type = choice(SENSOR_TYPES)
    sensor_id = choice(SENSOR_IDS[sensor_type])

    user_id = 1
    session_id = "{sensor_id}_{user_id}_{hash}".format(sensor_id=sensor_id,
                                                       user_id=user_id,
                                                       hash=utils.get_random_hash(16))

    created_at = int(time.time())
    inserted_at = int(time.time())

    context = "default"

    router_message = {'sensor_id': sensor_id,
                      'sensor_type': sensor_type,
                      'session_id': session_id,
                      'inserted_at': inserted_at,
                      'created_at': created_at,
                      'type': message_type,
                      'context': context,
                      'sensor_position': utils.get_random_sensor_position()
                      }

    if message_type == 'image_rgb':
        router_message.update({'image_rgb': utils.get_random_image(IMAGE_WIDTH,
                                                                   IMAGE_HEIGHT)})
    elif message_type == 'skeleton':
        router_message.update({'image_rgb': utils.get_random_skeleton()})

    return router_message
