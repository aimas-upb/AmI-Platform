import httplib
import logging
import requests
from unittest import TestCase

from httpretty import HTTPretty
from nose.tools import eq_

from lib import log
from lib.dashboard_cache import DashboardCache
from test.pipeline.messages import MEASUREMENTS_MESSAGE_SKELETON
from pipeline.room_position import RoomPosition

STATUS_OK = 200


class ApiTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super(ApiTest, cls).setUpClass()
        cls.dashboard_cache = DashboardCache()
        log.setup_logging(level=logging.DEBUG)

    def _skeleton_message(self):
        return MEASUREMENTS_MESSAGE_SKELETON

    def test_latest_subject_positions(self):
        message = self._skeleton_message()
        RoomPosition().process_message(message)
        path = 'latest_subject_positions/%s' % message['sensor_id']
        full_path = "http://127.0.0.1:8000/%s" % path
        HTTPretty.enable()
        HTTPretty.register_uri(HTTPretty.GET, full_path)
        response = requests.get(full_path)
        HTTPretty.disable()
        eq_(response.status_code, STATUS_OK,
            'Response has status_code: %s' % response.status_code)
