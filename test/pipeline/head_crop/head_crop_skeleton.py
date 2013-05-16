import logging
import time
from unittest import TestCase

from mock import patch
from nose.tools import eq_
from PIL import Image

from lib import log
from pipeline.head_crop import HeadCrop
from core.parallel_pdu import ParallelPDU
from message_factory import image_message,skeleton_message

class HeadCropSkeletonTest(TestCase):

    def setUp(self):
        super(HeadCropSkeletonTest, self).setUp()
        self.hc = HeadCrop()

    @classmethod
    def setUpClass(cls):
        super(HeadCropSkeletonTest, cls).setUpClass()
        log.setup_logging(level=logging.DEBUG)
    
    @patch.object(ParallelPDU, 'process_message')
    def test_image_firtst(self, process_message): 
        #an image first       
        rgb1 = image_message('daq-01', 10, (1,1))
        self.hc.process_message(rgb1)
        
        #adding a skeleton
        skeleton1 = skeleton_message('daq-01', 20)        
        self.hc.process_message(skeleton1)
        
        #a new image
        rgb2 = image_message('daq-01', 30, (1,2))
        self.hc.process_message(rgb2)
        
        #finally a new skeleton
        skeleton2 = skeleton_message('daq-01', 40)        
        self.hc.process_message(skeleton1)

        eq_(process_message.call_count, 4)
        
        _expect(process_message.call_args_list[0], rgb1['image_rgb'], None)
        _expect(process_message.call_args_list[1], rgb1['image_rgb'], skeleton1['skeleton_2D'])
        _expect(process_message.call_args_list[2], rgb2['image_rgb'], skeleton1['skeleton_2D'])
        _expect(process_message.call_args_list[3], rgb2['image_rgb'], skeleton2['skeleton_2D'])

    def _test_skeleton_first(self, process_message):
        #skeleton first
        skeleton = skeleton_message('daq-01')
                
        self.hc.process_message(skeleton)
        eq_(process_message.call_count, 1)
        _expect(process_message.call_args, None, skeleton['skeleton_2D'])        
    
        rgb1 = image_message('daq-01', 10, (4,4))
        process_message.reset_mock()
        self.hc.process_message(rgb1)
        eq_(process_message.call_count, 1)
        _expect(process_message.call_args, rgb1['image_rgb'], skeleton['skeleton_2D'])

    
    def _test_two_daqs(self, process_message):
        return
        rgb1 = image_message('daq-01', 10, (4,4))
        skeleton2 = skeleton_message('daq-02')
        
        self.hc.process_message(rgb1)
        self.hc.process_message(skeleton2)
        eq_(process_message.call_count, 2)
        _expect(process_message.call_args_list[0], rgb1['image_rgb'], None)
        _expect(process_message.call_args_list[1], None, skeleton2['skeleton_2D'])
        
        

def _expect(call, last_image, last_skeleton):
    hack = _get_hack_message(call)
    eq_(hack['last_skeleton'], last_skeleton)
    eq_(hack['last_image'], last_image)
         
def _get_hack_message(call):
    a, _ = call
    return a[0].get('hack', None)
        
        
        
         
        
    
