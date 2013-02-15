import logging

from nose.plugins.attrib import attr
from nose.tools import ok_, eq_

from core import PipelineTest
from pipeline.router import Router
from pipeline.head_crop import HeadCrop
from pipeline.face_recognition import FaceRecognition
from pipeline.room import Room

logger = logging.getLogger(__name__)

class TestAirConditioningWillBeTurnedOnForAndrei(PipelineTest):
    """ Given a dump with Andrei monkeying around in front of the Kinect,
    test that the air conditioning is indeed turned on. """
    
    PDUs = [Router, HeadCrop, FaceRecognition, Room]
    DATA_FILE = '/tmp/andrei2.txt'
    
    def setUp(self):
        super(TestAirConditioningWillBeTurnedOnForAndrei, self).setUp()
        logging.basicConfig(level=logging.DEBUG)
    
    @attr('pipeline', 'slow')
    def test_that_pipeline_test_works_ok(self):
        self._test_pipeline()
    
    def check_results(self):
        """ We check that room gave the command to IPPower to turn on one port
        of it (assuming that it's the port of the air conditioning system). """
        
        ip_power = self.queue_contents('ip-power')
        
        ok_(len(ip_power) > 0, "Andrei's presence should trigger at least "
                               "one action for the ip-power module")
        
        for msg in ip_power:
            eq_(msg.get('cmd'), 'on', "Andrei's presence should trigger a port "
                                      "of the ip power switch to be on")