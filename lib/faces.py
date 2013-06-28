import logging
from os import listdir

import cv

from core.constants import PROJECT_PATH


def _face_detect(opencv_image, config='haarcascade_frontalface_default'):
    # Load the data structure for Haar Cascade detector in memory
    haar_cascade = cv.Load(
        '{project_path}/resources/opencv_detectors/{config}'.format(
            project_path=PROJECT_PATH, config=config))

    # Even though the face detector from OpenCV has been trained on 20 x 20,
    # sending 20 x 20 images for face recognition to the BetaFace API
    # will result in nothing useful.
    min_size = (100, 100)
    faces = cv.HaarDetectObjects(opencv_image,
                                 haar_cascade,
                                 cv.CreateMemStorage(),
                                 min_size=min_size)

    return faces


def face_detect(image, config='haarcascade_frontalface_default'):
    """ Detects whether in the given image (PIL image) there are any faces
        or not using the OpenCV Haar cascade detector. """
    # Save the PIL image to disk and re-load it into IplImage format for
    # OpenCV. I know this is a terrible hack but we can take care of this
    # as an in-memory conversion later.
    from files import random_file_name
    temp_file = random_file_name('jpg')
    image.save(temp_file)
    opencv_image = cv.LoadImage(temp_file, cv.CV_LOAD_IMAGE_COLOR)
    return _face_detect(opencv_image, config)


def voting_face_detect(image, delta=20):
    """ Runs all detectors on an image and returns the most voted one.
    """
    configs = [config for config in listdir("%s/resources/opencv_detectors" %
                                            PROJECT_PATH)]

    from files import random_file_name
    temp_file = random_file_name('jpg')
    image.save(temp_file)
    opencv_image = cv.LoadImage(temp_file, cv.CV_LOAD_IMAGE_COLOR)

    results = [_face_detect(opencv_image, config) for config in configs]
    logging.debug('found results %s' % zip(configs, results))

    results = filter(lambda x: len(x) != 0, results)
    all_results = []
    for r in results:
        all_results.extend([r[0]])

    votes = [0] * len(all_results)

    logging.debug('found nb results %s' % len(all_results))

    if len(votes) == 0:
        return []
    if len(configs) == 1:
        return all_results[0]

    for i in range(len(all_results)):
        for j in range(i + 1, len(all_results)):
            if similar(all_results[i][0], all_results[j][0], delta):
                votes[i] += 1

    logging.debug('found votes %s' % votes)

    max_votes = max(votes)
    if max_votes < 1:
        return []

    return results[votes.index(max_votes)]


def similar(r1, r2, delta):
    (x1, y1, w1, h1) = r1
    (x2, y2, w2, h2) = r2

    l = [x1 - x2, y1 - y2, x1 + w1 - x2 - w2, y1 + h1 - y2 - h2]

    return all(abs(v) <= delta for v in l)
