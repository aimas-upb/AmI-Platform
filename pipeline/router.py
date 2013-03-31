import time

from core import PDU

from lib.log import setup_logging

class Router(PDU):
    """ PDU that routes incoming measurements from sensors to the
        actual processing pipelines """

    QUEUE = 'measurements'

    def process_message(self, message):
        # Route messages towards mongo-writer

        # created_at should be normally set as close to the data generation
        # as possible and should be the timestamp that the measurement
        # was phisically generated. Since this is not always possible, the
        # default is the time of entry in the pipeline.
        message['created_at'] = message.get('created_at', int(time.time()))

        self.send_to('mongo-writer', message)

        if message['type'] in ['image_rgb', 'skeleton']:
            self.send_to('head-crop', message)

        # self.send_to('recorder', message)

        # Only send to room position if it's a Kinect skeleton
        if message['sensor_type'] == 'kinect' and message['type'] == 'skeleton':
            self.send_to('room-position', message)

        # Only send to dashboard if it's a Kinect RGB image
        if message['sensor_type'] == 'kinect' and message['type'] in ['image_rgb', 'skeleton']:
            self.send_to('dashboard', message)

if __name__ == "__main__":
    setup_logging()
    module = Router()
    module.run()
