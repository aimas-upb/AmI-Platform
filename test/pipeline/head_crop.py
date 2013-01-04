import time
from unittest import TestCase

from mock import MagicMock, patch
from nose.tools import ok_, eq_

from pipeline.head_crop import HeadCrop

class HeadCropTest(TestCase):
    
    def _image_message(self):
        return {
            'sensor_type': 'kinect_rgb',
            'image': 'A' * (640 * 480 * 3 * 4/3), 
            'width': 640,
            'height': 480 
        }
    
    def _skeleton_message(self):
        return {
            'sensor_type': 'kinect',
            'skeleton_2d': {'head': {1.0, 2.0}, 'neck': {3.0, 4.0}} 
        }

    @patch.object(HeadCrop, 'send_to')
    # Because we don't have image + skeleton, face detection should
    # be called, and make sure it doesn't return anything useful
    @patch.object(HeadCrop, 'face_detect', return_value = None)
    @patch.object(HeadCrop, 'crop_head', return_value = None)
    def test_sole_image_without_face_doesnt_sent_to_recognition(self, crop_head, face_detect, send_to):
        pdu = HeadCrop()
        pdu.process_message(self._image_message())
        face_detect.assert_called_once_with()
        eq_(crop_head.call_count, 0, "crop_head should only be called if it has "
                                   "a corresponding image and skeleton")
        eq_(send_to.call_count, 0, "send_to should only be called if it has "
                                   "a corresponding image and skeleton")
        
    @patch.object(HeadCrop, 'send_to')
    @patch.object(HeadCrop, 'face_detect', return_value = None)
    @patch.object(HeadCrop, 'crop_head', return_value = None)
    def test_sole_skeleton_doesnt_send_to_recognition(self, crop_head, face_detect, send_to):
        pdu = HeadCrop()
        pdu.process_message(self._skeleton_message())
        eq_(crop_head.call_count, 0, "crop_head should only be called if it has "
                                   "a corresponding image and skeleton")
        eq_(send_to.call_count, 0, "send_to should only be called if it has "
                                   "a corresponding image and skeleton")
        eq_(face_detect.call_count, 0, "face_detect should only be called if it has "
                                   "a corresponding image and skeleton")
        
        
    @patch.object(HeadCrop, 'send_to')
    @patch.object(HeadCrop, 'face_detect', return_value = None)
    @patch.object(HeadCrop, 'crop_head', return_value = None)
    def test_one_image_and_one_skeleton_not_close_enough(self, crop_head, face_detect, send_to):
        pdu = HeadCrop()
        pdu.process_message(self._skeleton_message())
        time.sleep(pdu.MAX_TIME)
        pdu.process_message(self._image_message())
        face_detect.assert_called_once_with()
        eq_(crop_head.call_count, 0, "crop_head should only be called if it has "
                                   "a corresponding image and skeleton")
        eq_(send_to.call_count, 0, "send_to should only be called if it has "
                                   "a corresponding image and skeleton")
       
    @patch.object(HeadCrop, 'send_to')
    @patch.object(HeadCrop, 'face_detect', return_value = None)
    @patch.object(HeadCrop, 'crop_head', return_value = {})
    def test_one_image_and_one_skeleton_close_enough(self, crop_head, face_detect, send_to):
        pdu = HeadCrop()
        pdu.process_message(self._skeleton_message())
        pdu.process_message(self._image_message())
        eq_(face_detect.call_count, 0, "face_detect should only be called if it has "
                                   "a corresponding image and skeleton")
        send_to.assert_called_once_with('face-recognition', {})
        crop_head.assert_called_once_with()
        
    
    
