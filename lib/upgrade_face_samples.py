# Reads images from 'face_samples/person_name' and
# uploads them to BetaFace API.

import os

from pipeline.upgrade_face_samples import UpgradeFaceSamples

PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))
foldername = '%s/face_samples/' % PROJECT_PATH
person_names = os.listdir(foldername)


pdu = UpgradeFaceSamples()

for person_name in person_names:
    path = "%s%s" % (foldername, person_name)
    print(">>> Uploading %d images for %s ..." % (len(os.listdir(path)),
                                                  person_name))
    i = 0
    for image in os.listdir(path):
        image_path = "%s/%s" % (path, image)
        print("%d: Fedding face sample %s as an example for %s" %
              (i, image, person_name))
        result = pdu.api.upload_face(image_path, person_name)
        print("\t%s" % result)
        i = i + 1
