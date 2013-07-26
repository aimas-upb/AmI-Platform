import logging

from nose.plugins.attrib import attr
from nose.tools import ok_

from core import PipelineTest
from core.constants import PROJECT_PATH
from pipeline.face_recognition import FaceRecognition
from pipeline.head_crop import HeadCrop
from pipeline.router import Router

logging.basicConfig(level=logging.DEBUG)


class TestRecognition(PipelineTest):
    """#1110 - Test that I am in front of the camera and it detects me."""

    PDUs = [Router, HeadCrop, FaceRecognition]
    DATA_FILE = '%s/dumps/diana.txt' % PROJECT_PATH
    NB_MIN_EXPECTED_EVENTS = 1
    DELAY_UNTIL_MESSAGES_PROPAGATE = 30

    @attr('pipeline', 'slow')
    def test_that_pipeline_test_works_ok(self):
        self._test_pipeline()

    def check_results(self):
        events = []

        event = self._queue_system.get('room', 1)
        while (event is not None):
            events.append(event)
            event = self._queue_system.get('room', 1)

        ok_(len(events) >= self.NB_MIN_EXPECTED_EVENTS)
