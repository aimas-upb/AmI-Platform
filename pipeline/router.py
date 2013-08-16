import time

from mongoengine import connect

from core import PDU, settings
from lib.log import setup_logging
from lib.s3 import save_image
from models.experiment import Experiment


class Router(PDU):
    """ PDU that routes incoming measurements from sensors to the
        actual processing pipelines """

    QUEUE = 'measurements'

    def __init__(self, **kwargs):
        super(Router, self).__init__(**kwargs)
        connect('experiments', host=settings.MONGO_SERVER)

    def process_message(self, message):
        # Route messages towards mongo-writer

        # created_at should be normally set as close to the data generation
        # as possible and should be the timestamp that the measurement
        # was phisically generated. Since this is not always possible, the
        # default is the time of entry in the pipeline.
        message['created_at'] = message.get('created_at', int(time.time()))

        self.send_to('mongo-writer', message)

        # Images & skeletons should be sent to head-crop
        if message['type'] in ['image_rgb', 'skeleton']:
            self.send_to('head-crop', message)

        if message['type'] == 'image_rgb':
            save_image(message['image_rgb']['image'],
                       int(message['image_rgb']['width']),
                       int(message['image_rgb']['height']),
                       prefix='RAW_', decoder_name='jpg')

        # If there is at least one active experiment, send them to
        # recorder. Otherwise, prevent bandwidth waste :)
        active_experiments = Experiment.get_active_experiments()
        if len(active_experiments) > 0:
            self.send_to('recorder', message)

        # Only send to room position if it's a Kinect skeleton
        if (message['sensor_type'] == 'kinect' and
            message['type'] == 'skeleton'):
                self.send_to('room-position', message)

        # Only send to dashboard if it's a Kinect RGB image
        if (message['sensor_type'] == 'kinect' and
            message['type'] in ['image_rgb', 'skeleton']):
                self.send_to('dashboard', message)

if __name__ == "__main__":
    setup_logging()
    module = Router()
    module.run()
