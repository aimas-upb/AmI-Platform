from factory import Factory

from core.constants import IMAGE_WIDTH, IMAGE_HEIGHT
from factories import utils


def UpgradeFaceSamplesFactory(person_name='andrei'):
    """ Generates a 'upgrade-face-samples' message which will be processed by
    UpgradeFaceSamples PDU.

    Example:
    {
    'head_image': {
        'image': 'AAAA',
        'width':640,
        'height': 480
        },
    'person_name': 'andrei@amilab.ro'
    }
    """
    return {'head_image': {
                           'image': utils.get_random_image(IMAGE_WIDTH / 10,
                                                           IMAGE_HEIGHT / 10),
                           'width': IMAGE_WIDTH / 10,
                           'height': IMAGE_HEIGHT / 10},
            'person_name': person_name}
