from lib.opencv import crop_face_from_image
import os
from core.constants import PROJECT_PATH
from PIL import Image
from termcolor import cprint
from unittest import TestCase
from lib.s3 import upload_to_s3

from core.constants import (SKYBIOMETRY_NAMESPACE, SKYBIOMETRY_API_KEY,
                            SKYBIOMETRY_API_SECRET)
from sky_biometrics.face_client import FaceClient


class TestHeadCrop(TestCase):
    def test_face_cropped_ok(self):
        """Detect faces from a folder of Kinect face images."""
        image_folder = "%s/test/unit/dataset" % PROJECT_PATH
        images = [image for image in os.listdir(image_folder)
                  if os.path.isfile("%s/%s" % (image_folder, image))]

        count = 0
        self.remove_dir_contents("%s/%s" % (image_folder, "results"))
        for image_file in images:
            print("Searching faces in %s ..." % image_file),
            image = Image.open("%s/%s" % (image_folder, image_file))
            cropped_head = crop_face_from_image(image)
            if cropped_head:
                cprint(' OK ', 'green'),
                cropped_head_path = "%s/results/%s" % (image_folder, image_file)
                cropped_head.save(cropped_head_path)
                self.recognize(cropped_head_path)
                count = count + 1
            else:
                cprint(' FAIL', 'red')
        cprint(" > DONE! Found %d faces in %d images." %
               (count, len(images)), 'yellow')

    def remove_dir_contents(self, folder_path):
        for the_file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception, e:
                print e

    def recognize(self, image_path):
        try:
            api = FaceClient(SKYBIOMETRY_API_KEY, SKYBIOMETRY_API_SECRET)
            image_url = upload_to_s3(image_path)
            response = api.faces_recognize('all', image_url,
                                       namespace=SKYBIOMETRY_NAMESPACE)

            tags = response['photos'][0]['tags']
            if tags:
                matches = tags[0]['uids']
                cprint("Matches: %r" % matches, 'green')
            else:
                cprint("No matches!", 'red')
        except Exception as e:
            cprint(e, 'red')
