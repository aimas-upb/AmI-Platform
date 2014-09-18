import base64
import logging
import time
from unittest import TestCase

from mock import patch, ANY
from nose.tools import eq_
from PIL import Image

from core.constants import PROJECT_PATH
from factories import RouterFactory
from lib import log
from lib.session_store import SessionStore
from pipeline import head_crop
from pipeline.head_crop import HeadCrop, MAX_TIME
from lib.image import image_to_base64


class TestHeadCrop(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestHeadCrop, cls).setUpClass()
        log.setup_logging(level=logging.DEBUG)

    @patch.object(HeadCrop, 'send_to')
    # Because we don't have image + skeleton, face detection should
    # be called, and make sure it doesn't return anything useful
    @patch('pipeline.head_crop._crop_head_using_face_detection', return_value=None)
    @patch('pipeline.head_crop._crop_head_using_skeleton', return_value=None)
    def test_sole_image_without_face_doesnt_sent_to_recognition(self, skeleton, face_detect, send_to):
        pdu = HeadCrop(debug=True)
        message = RouterFactory('image_rgb')
        pdu.process_message(message)

        face_detect.assert_called_once_with(message['image_rgb'])
        eq_(skeleton.call_count, 0, "crop_head should only be called if it has "
                                   "a corresponding image and skeleton")
        eq_(send_to.call_count, 0, "send_to should only be called if it has "
                                   "a corresponding image and skeleton")

    @patch.object(HeadCrop, 'send_to')
    @patch('pipeline.head_crop._crop_head_using_face_detection', return_value=None)
    @patch('pipeline.head_crop._crop_head_using_skeleton', return_value=None)
    def test_sole_skeleton_doesnt_send_to_recognition(self, skeleton, face_detect, send_to):
        pdu = HeadCrop(debug=True)
        message = RouterFactory('skeleton')
        pdu.process_message(message)

        eq_(skeleton.call_count, 0, "crop_head should only be called if it has "
                                   "a corresponding image and skeleton")
        eq_(send_to.call_count, 0, "send_to should only be called if it has "
                                   "a corresponding image and skeleton")
        eq_(face_detect.call_count, 0, "face_detect should only be called if it has "
                                   "a corresponding image and skeleton")

    @patch.object(HeadCrop, 'send_to')
    @patch('pipeline.head_crop._crop_head_using_face_detection', return_value=None)
    @patch('pipeline.head_crop._crop_head_using_skeleton', return_value=None)
    def test_one_image_and_one_skeleton_not_close_enough(self, skeleton, face_detect, send_to):
        pdu = HeadCrop(debug=True)

        skeleton_message = RouterFactory('skeleton')
        pdu.process_message(skeleton_message)
        time.sleep(MAX_TIME)
        image_message = RouterFactory('image_rgb')
        pdu.process_message(image_message)

        face_detect.assert_called_once_with(image_message['image_rgb'])
        eq_(skeleton.call_count, 0, "crop_head should only be called if it has "
                                   "a corresponding image and skeleton")
        eq_(send_to.call_count, 0, "send_to should only be called if it has "
                                   "a corresponding image and skeleton")

    @patch.object(HeadCrop, 'send_to')
    @patch('pipeline.head_crop._crop_head_using_face_detection', return_value=None)
    @patch('pipeline.head_crop._crop_head_using_skeleton', return_value=Image.frombuffer('RGB', (1, 1), base64.b64decode('AAAA'), 'raw', 'RGB', 0, 1))
    def test_one_image_and_one_skeleton_close_enough(self, skeleton, face_detect, send_to):
        pdu = HeadCrop(debug=True)
        skeleton_message = RouterFactory('skeleton')
        pdu.process_message(skeleton_message)
        image_message = RouterFactory('image_rgb')
        pdu.process_message(image_message)

        eq_(face_detect.call_count, 0, "face_detect should only be called if "
            "it has a corresponding image and skeleton")
        skeleton.assert_called_once_with(image_message['image_rgb'],
                                         skeleton_message['skeleton_3D'])
        send_to.assert_called_once_with('face-recognition', ANY)

    def head_crop(self, file_in):
        """Returns None or a rectangle."""

    def test_face_cropped_ok(self):
        """Detect faces from a folder of Kinect images.

        If this test fails it means that:
            - our face detection algorithm has improved and we detect faces in
            much more images than the beginning.
            Uncomment line 119, run test again and check output images!
            Update face_images array! :)
            or
            - our face detection algorithm is buggy and it does not recognize
            the same images as the beginning.
        """
        from lib.opencv import crop_face_from_image
        from os import listdir

        image_folder = "%s/headcrop_dataset/" % PROJECT_PATH
        images = [image for image in listdir(image_folder)
                  if not image.endswith('_result.jpg')]
        face_images = ['2.jpg', '3.jpg', '11.jpg', '12.jpg', '14.jpg',
                       '18.jpg', '20.jpg', '21.jpg']

        for image_file in images:
            image = Image.open("%s/%s" % (image_folder, image_file))
            cropped_head = crop_face_from_image(image)
            if cropped_head is not None:
                #cropped_head.save("%s/%s_result.jpg" % (image_folder, image_file))
                self.assertIn(image_file, face_images)
            else:
                self.assertNotIn(image_file, face_images)

    @patch.object(SessionStore, "set")
    def test_send_message_to_redis_when_cropped_head(self, session_store_mock):
        orig_fn = head_crop.crop_head
        head_crop.crop_head = one_by_one_image

        pdu = HeadCrop(debug=True)
        image_message = RouterFactory('image_rgb')
        pdu.process_message(image_message)
        time.sleep(1.0)

        sid = image_message['session_id']
        t = image_message['created_at']
        info = {'head': one_by_one_image(None)}

        session_store_mock.assert_called_once_with(sid, t, info)
        head_crop.crop_head = orig_fn


def one_by_one_image(_):
    return image_to_base64(Image.frombuffer(
        'RGB', (1, 1), base64.b64decode('AAAA'), 'raw', 'RGB', 0, 1))
