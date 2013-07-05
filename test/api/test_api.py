import json
import logging
import random
import string
import time
from unittest import TestCase

from httpretty import HTTPretty
from nose.tools import eq_, ok_
import redis
import requests
from webtest import TestApp

from api import api
from core import settings
from factories import RouterFactory
from lib import log
from lib.dashboard_cache import DashboardCache
from lib.session_store import SessionStore
from lib.processed_session_store import ProcessedSessionStore

STATUS_OK = 200


class ApiTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super(ApiTest, cls).setUpClass()
        cls.dashboard_cache = DashboardCache()
        log.setup_logging(level=logging.DEBUG)

    def setUp(self):
        # Clean-up databases
        redis.StrictRedis(host=settings.REDIS_SERVER,
                          port=settings.REDIS_PORT,
                          db=settings.REDIS_SESSION_DB).flushdb()
        redis.StrictRedis(host=settings.REDIS_SERVER,
                          port=settings.REDIS_PORT,
                          db=settings.REDIS_PROCESSED_SESSION_DB).flushdb()

    def _skeleton_message(self):
        return RouterFactory('skeleton')

    def test_latest_subject_positions(self):
        # Keep this import here in order to avoid OpenCV imports
        from pipeline.room_position import RoomPosition

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

    def test_raw_sessions_endpoint(self):
        self._test_endpoint('raw')

    def test_processed_sessions_endpoint(self):
        self._test_endpoint('processed')

    def _test_endpoint(self, endpoint_name):
        if endpoint_name == 'raw':
            store = SessionStore()
        elif endpoint_name == 'processed':
            store = ProcessedSessionStore()

        # Create a HTTP-ish client over the WSGI app exposed by Bottle
        app = TestApp(api.app)

        # Populate Redis with sessions
        created_sessions = self._create_sessions(store)

        # Request the sessions via API
        response = app.get('/sessions/%s' % endpoint_name)
        returned_sessions = json.loads(response.body)['sessions']

        # Can't use self.assertDictEqual() because of str vs. utf8 str
        # and because timestamps are "approximately" equal - see
        # _round_down(time) in session_store.
        eq_(set(created_sessions.keys()), set(returned_sessions.keys()),
            "There should be exactly the same sessions in the HTTP response")
        for session_id in created_sessions.iterkeys():
            ok_(abs(created_sessions[session_id]-
                   returned_sessions[session_id]) < 100,  # 100 ms
                "Last updated at should be equal for created "
                "and returned session")

    def _create_sessions(self, store):
        """ Create some sessions in a given store, and return a dictionary
        mapping their ids to their last update. """

        N = random.randint(5, 10)
        sessions = {}

        for _ in xrange(N):
            sid = ''.join([random.choice(string.hexdigits)
                           for _ in xrange(16)])
            t = int(time.time() * 1000) - random.randint(100, 1000)
            store.set(sid, t, {})
            sessions[sid] = t

        return sessions
