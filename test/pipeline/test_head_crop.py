import base64
import logging
import time
from unittest import TestCase

from mock import patch
from nose.tools import eq_
from PIL import Image

from lib import log
from lib.sessions_store import SessionsStore
from messages import MEASUREMENTS_MESSAGE_IMAGE_RGB
from pipeline.head_crop import HeadCrop


class TestHeadCrop(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super(TestHeadCrop, cls).setUpClass()
        log.setup_logging(level=logging.DEBUG)
    
    def _image_message(self):
        return {
            'sensor_type': 'kinect',
            'type': 'image_rgb',
            'image_rgb': {
                'image': 'A' * (640 * 480 * 3 * 4/3), 
                'width': 640,
                'height': 480
            } 
        }
    
    def _skeleton_message(self):
        return {
            'sensor_type': 'kinect',
            'type': 'skeleton',
            'skeleton_2D': {'head': {1.0, 2.0}, 'neck': {3.0, 4.0}} 
        }
    
    @patch.object(HeadCrop, 'send_to')
    # Because we don't have image + skeleton, face detection should
    # be called, and make sure it doesn't return anything useful
    @patch('pipeline.head_crop._crop_head_using_face_detection', return_value = None)
    @patch('pipeline.head_crop._crop_head_using_skeleton', return_value = None)
    def test_sole_image_without_face_doesnt_sent_to_recognition(self, skeleton, face_detect, send_to):
        return
        
        pdu = HeadCrop()
        pdu.process_message(self._image_message())
        face_detect.assert_called_once_with()
        eq_(skeleton.call_count, 0, "crop_head should only be called if it has "
                                   "a corresponding image and skeleton")
        eq_(send_to.call_count, 0, "send_to should only be called if it has "
                                   "a corresponding image and skeleton")
        
    @patch.object(HeadCrop, 'send_to')
    @patch('pipeline.head_crop._crop_head_using_face_detection', return_value = None)
    @patch('pipeline.head_crop._crop_head_using_skeleton', return_value = None)
    def test_sole_skeleton_doesnt_send_to_recognition(self, skeleton, face_detect, send_to):
        return
        
        pdu = HeadCrop()
        pdu.process_message(self._skeleton_message())
        eq_(skeleton.call_count, 0, "crop_head should only be called if it has "
                                   "a corresponding image and skeleton")
        eq_(send_to.call_count, 0, "send_to should only be called if it has "
                                   "a corresponding image and skeleton")
        eq_(face_detect.call_count, 0, "face_detect should only be called if it has "
                                   "a corresponding image and skeleton")
        
        
    @patch.object(HeadCrop, 'send_to')
    @patch('pipeline.head_crop._crop_head_using_face_detection', return_value = None)
    @patch('pipeline.head_crop._crop_head_using_skeleton', return_value = None)
    def test_one_image_and_one_skeleton_not_close_enough(self, skeleton, face_detect, send_to):
        return
        
        pdu = HeadCrop()
        pdu.process_message(self._skeleton_message())
        time.sleep(pdu.MAX_TIME)
        pdu.process_message(self._image_message())
        face_detect.assert_called_once_with()
        eq_(skeleton.call_count, 0, "crop_head should only be called if it has "
                                   "a corresponding image and skeleton")
        eq_(send_to.call_count, 0, "send_to should only be called if it has "
                                   "a corresponding image and skeleton")
       
    @patch.object(HeadCrop, 'send_to')
    @patch('pipeline.head_crop._crop_head_using_face_detection', return_value = None)
    @patch('pipeline.head_crop._crop_head_using_skeleton', return_value = Image.frombuffer('RGB', (1, 1), base64.b64decode('AAAA')))
    def test_one_image_and_one_skeleton_close_enough(self, skeleton, face_detect, send_to):
        # TODO(andrei): seems to me like this doesn't get run properly
        # due to the fact that it's a parallel PDU. Suggestion: let's implement
        # a "debug" mode for parallel PDUs without a worker pool.
        return
    
        pdu = HeadCrop()
        pdu.process_message(self._skeleton_message())
        pdu.process_message(self._image_message())
        time.sleep(1.0)
        eq_(face_detect.call_count, 0, "face_detect should only be called if it has "
                                   "a corresponding image and skeleton")
        face_recognition_message = {
            'head_image': {
                'width': 1, 
                'image': 'AAAA', 
                'height': 1
            }
        }
        send_to.assert_called_once_with('face-recognition', 
                                        face_recognition_message)
        skeleton.assert_called_once_with()
    
    def head_crop(self, file_in):
        '''returns NONE or a rectangle'''

    def test_face_cropped_ok(self):
        from lib.opencv import crop_face_from_image
        from os import listdir
        image_folder = "/home/ami/AmI-Platform/headcrop_dataset"
        images = [ image for image in listdir(image_folder) if not image.endswith('_result.jpg')]

        for image_file in images:
            image = Image.open("%s/%s" % (image_folder,image_file))
            logging.debug("processing image %s" % image_file)
            cropped_head = crop_face_from_image(image)
            if cropped_head is not None:
                cropped_head.save("%s/%s_result.jpg" % (image_folder, image_file))
                print '.'

    @patch.object(SessionsStore, "set")
    def test_send_message_to_redis_when_cropped_head(self, sessions_store_mock):
        pdu = HeadCrop()
        message = MEASUREMENTS_MESSAGE_IMAGE_RGB
        pdu.process_message(message)
        sid = message['session_id']
        time = message['created_at']
        mappings = {'head': pdu.heavy_preprocess}
        sessions_store_mock.assert_called_once_with(sid, time, mappings)
