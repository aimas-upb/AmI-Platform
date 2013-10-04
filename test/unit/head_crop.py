from lib.opencv import crop_face_from_image
import os
from core.constants import PROJECT_PATH
from PIL import Image
from unittest import TestCase
from lib.s3 import upload_to_s3

from core.constants import (SKYBIOMETRY_NAMESPACE, SKYBIOMETRY_API_KEY,
                            SKYBIOMETRY_API_SECRET)
from sky_biometrics.face_client import FaceClient


class TestHeadCrop(TestCase):
    def test_face_cropped_ok(self):
        """Detect faces from a folder of Kinect face images.

        HOW TO TEST HEAD CROP ON A GIVEN IMAGE DATASET:
            - just place the images in PROJECT_PATH/test/unit/dataset and run
            this test:
            $ nosetests head_crop.py --nocapture.
            Use "--nocapture" option to see all output. Results images will be
            stored under PROJECT_PATH/test/unit/dataset/results folder.
        """
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
                print(' OK '),
                cropped_head_path = "%s/results/%s" % (image_folder, image_file)
                cropped_head.save(cropped_head_path)
                self.recognize(cropped_head_path)
                count = count + 1
            else:
                print(' FAIL')
        print(" > DONE! Found %d faces in %d images." % (count, len(images)))

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
                print("Matches: %r" % matches)
                print(" => %s" % self._get_best_match(matches))
            else:
                print("No matches!")
        except Exception as e:
            print(e)

    def _get_best_match(self, matches):
        """Args:
                matches: a list of dicts representing the SkyBIometry matches.
                Example:
                    [{u'confidence': 51, u'uid': u'andrei@amilab-test2'},
                    {u'confidence': 48, u'uid': u'diana@amilab-test2'}]
        """
        best_confidence = 0
        person = ''
        for match in matches:
            if match['confidence'] > best_confidence:
                best_confidence = match['confidence']
                person = match['uid']
        return person
