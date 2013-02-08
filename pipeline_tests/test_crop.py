
from nose.tools import ok_

from core import PipelineTest
from pipeline.router import Router
from pipeline.head_crop import HeadCrop

class TestCrop(PipelineTest):
    '''#110 - Test that I am in front of the camera and it crops my head'''
    
    PDUs = [Router, HeadCrop]
    DATA_FILE = '/tmp/andrei.txt'
    NB_MIN_EXPECTED_FACES = 1
    
    def test_that_pipeline_test_works_ok(self):
        self._test_pipeline()
    
    def check_results(self):
        nb_faces = 0
        while (self._queue_system.get('face-recognition', 1) is not None):
            nb_faces = nb_faces + 1
        
        ok_(nb_faces >= self.NB_MIN_EXPECTED_FACES)
        

