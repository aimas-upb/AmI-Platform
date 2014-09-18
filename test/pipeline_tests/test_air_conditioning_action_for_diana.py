import logging

from nose.plugins.attrib import attr
from nose.tools import ok_, eq_

from core import PipelineTest
from core.constants import PROJECT_PATH
from pipeline.router import Router
from pipeline.head_crop import HeadCrop
from pipeline.face_recognition import FaceRecognition
from pipeline.room import Room

logger = logging.getLogger(__name__)


class TestAirConditioningWillBeTurnedOffForDiana(PipelineTest):
    """ Given a dump with Diana monkeying around in front of the Kinect,
    test that the air conditioning is indeed turned off. """

    PDUs = [Router, HeadCrop, FaceRecognition, Room]
    DATA_FILE = '%s/dumps/diana-daq-02.txt' % PROJECT_PATH

    def setUp(self):
        super(TestAirConditioningWillBeTurnedOffForDiana, self).setUp()
        logging.basicConfig(level=logging.DEBUG)

    @attr('pipeline', 'slow')
    def test_that_pipeline_test_works_ok(self):
        self._test_pipeline()

    def check_results(self):
        """ We check that room gave the command to IPPower to turn off one port
        of it (assuming that it's the port of the air conditioning system)."""
        ip_power = self.queue_contents('ip-power')

        ok_(len(ip_power) > 0, "Diana's presence should trigger at least "
                               "one action for the ip-power module")

        for msg in ip_power:
            eq_(msg.get('cmd'), 'off', "Diana's presence should trigger a port"
                                      " of the ip power switch to be off")
