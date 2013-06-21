import array
import os
import uuid

from PIL import Image
from pybetaface.api import BetaFaceAPI

from core import PDU
from lib.log import setup_logging


class UpgradeFaceSamples(PDU):
    QUEUE = 'upgrade-face-samples'

    def __init__(self, **kwargs):
        super(UpgradeFaceSamples, self).__init__()
        self.api = BetaFaceAPI()

    def save_image_to_file(self, buffer, width, height, path):
        image_buffer = array.array('B', buffer).tostring()
        image_to_file = Image.frombuffer("RGB", (width, height),
                                         image_buffer)
        image_to_file.save(path)

    def process_message(self, message):
        """ Sends the face sample to BetaFaceAPI.

        Right now, these samples are coming from the face recognition module,
        whenever the recognition confidence is really high. """

        person_name = message['person_name']
        head_image = message['head_image']
        image = head_image['image']
        width = int(head_image['width'])
        height = int(head_image['height'])

        # Save image to file
        path = "/tmp/%s.jpg" % uuid.uuid4()
        self.save_image_to_file(image, width, height, path)
        self.logger.info("Saved face sample to file %s" % path)

        # Upload image to BetaFace API
        self.api.upload_face(path, person_name)
        self.logger.info("Fed face sample %s as an example for %s" %\
                         (path, person_name))

        os.remove(str(path))
        self.logger.info("Removed temporary file %s from disk" % str)

if __name__ == "__main__":
    setup_logging()
    module = UpgradeFaceSamples()
    module.run()
