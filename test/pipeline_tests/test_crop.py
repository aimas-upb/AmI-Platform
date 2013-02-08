import logging

logging.basicConfig(level=logging.DEBUG)

from nose.tools import ok_

from core import PipelineTest
from pipeline.router import Router
from pipeline.head_crop import HeadCrop

logger = logging.getLogger(__name__)

class TestCrop(PipelineTest):
    '''#110 - Test that I am in front of the camera and it crops my head'''
    
    PDUs = [Router, HeadCrop]
    DATA_FILE = '/tmp/andrei.txt'
    NB_MIN_EXPECTED_FACES = 10
    DELAY_UNTIL_MESSAGES_PROPAGATE = 30
    
    def test_that_pipeline_test_works_ok(self):
        self._test_pipeline()
    
    def check_results(self):
        logger.info("Still %s alive pdu threads" % self.alive_pdus())
        nb_faces = 0
        while (self._queue_system.get('face-recognition', 1) is not None):
            nb_faces = nb_faces + 1
        
        ok_(nb_faces >= self.NB_MIN_EXPECTED_FACES)
        