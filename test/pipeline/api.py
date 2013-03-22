import httplib
import logging
from unittest import TestCase

from nose.tools import eq_

from lib import log
from test.pipeline.messages import MEASUREMENTS_MESSAGE_SKELETON
from pipeline.room_position import RoomPosition


class ApiTest(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super(ApiTest, cls).setUpClass()
        log.setup_logging(level=logging.DEBUG)
    
    def _skeleton_message(self):
        return MEASUREMENTS_MESSAGE_SKELETON

    def test_latest_subject_positions(self):
        message = self._skeleton_message()
        RoomPosition().process_message(message)
        path = '/latest_subject_positions/%s' % message['sensor_id']
        import pdb;pdb.set_trace()
        conn = httplib.HTTPConnection('127.0.0.1')
        conn.request('GET', path)
        response = conn.getresponse() 
        eq_(200, response.status_code)
