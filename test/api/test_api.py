from collections import defaultdict
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
from lib import log
from lib.dashboard_cache import DashboardCache
from lib.session_store import SessionStore
from lib.processed_session_store import ProcessedSessionStore
from test.pipeline.messages import MEASUREMENTS_MESSAGE_SKELETON

STATUS_OK = 200

class ApiTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super(ApiTest, cls).setUpClass()
        cls.dashboard_cache = DashboardCache()
        log.setup_logging(level=logging.DEBUG)

    def setUp(self):
        # Clean-up databases
        redis.StrictRedis(host = settings.REDIS_SERVER,
                          port = settings.REDIS_PORT,
                          db = settings.REDIS_SESSION_DB).flushdb()
        redis.StrictRedis(host = settings.REDIS_SERVER,
                          port = settings.REDIS_PORT,
                          db = settings.REDIS_PROCESSED_SESSION_DB).flushdb()

    def _skeleton_message(self):
        return MEASUREMENTS_MESSAGE_SKELETON

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
            # Get created measurements sorted descending by time
            created_measurements = sorted(created_sessions[session_id],
                                          key=lambda x: x['time'],
                                          reverse=True)
            returned_measurements = returned_sessions[session_id]

            eq_(len(created_measurements), len(returned_measurements),
                "Sessions returned through the API should contain the correct "
                "number of measurements attached to each other")

            for (m1, m2) in zip(created_measurements, returned_measurements):
                msg = "Returned sessions should have correct coordinates & time"
                ok_(abs(float(m1['X']) - float(m2['X'])) < 0.01, msg)
                ok_(abs(float(m1['Y']) - float(m2['Y'])) < 0.01, msg)
                ok_(abs(float(m1['Z']) - float(m2['Z'])) < 0.01, msg)
                eq_(int(m1['time']), int(m2['time']), msg)

    def _create_sessions(self, store):
        """ Create some sessions in a given store, and return a dictionary
        mapping their ids to their last update. """

        N = random.randint(5, 10)
        sessions = defaultdict(list)
        unique_times = set()

        for _ in xrange(N):
            sid = ''.join([random.choice(string.hexdigits)
                           for _ in xrange(16)])
            for _ in xrange(random.randint(5, 10)):
                t = int(time.time() * 1000) - random.randint(10000, 1000000)
                while t in unique_times:
                    t = int(time.time() * 1000) - random.randint(100, 1000)
                unique_times.add(t)
                X = 500 + random.random() * 100
                Y = 500 + random.random() * 100
                Z = 500 + random.random() * 100
                measurement = {'X': X, 'Y': Y, 'Z': Z, 'time': t}
                sessions[sid].append(measurement)
                store.set(sid, t, measurement)

        return sessions

    def test_raw_measurement(self):
        self._test_measurements('raw')
        
    def test_processed_measurement(self):
        self._test_measurements('processed')
    
    def _test_measurements(self, endpoint_name):
        if endpoint_name == 'raw':
            store = SessionStore()
        elif endpoint_name == 'processed':
            store = ProcessedSessionStore()
    
        # Create a HTTP-ish client over the WSGI app exposed by Bottle
        app = TestApp(api.app)
    
        # Populate Redis with sessions
        created_sessions = self._create_sessions(store)
        for sid in created_sessions.keys():
            measurements = self._populate_session(store, sid)
            for t in measurements.keys():
                # Request the sessions via API
                response = app.get('/measurements/%s?sid=%s&time=%s' % (endpoint_name, sid, t))
                returned_measurements = json.loads(response.body)['measurements']
        
                # Can't use self.assertDictEqual() because of str vs. utf8 str
                # and because timestamps are "approximately" equal - see
                # _round_down(time) in session_store.
                eq_(set(measurements[t].keys()), set(returned_measurements.keys()),
                    "There should be exactly the same measurements in the HTTP response")
                
                for key in measurements[t].iterkeys():
                    eq_(measurements[t][key], returned_measurements[key],
                        "Values should be equal in measurement")

    def _populate_session(self, store, sid):
        measurements = {}
        N = random.randint(1,3)
        t = int(time.time() * 100) * 10
        for _ in xrange(N):
            key = ''.join([random.choice(string.hexdigits)
                           for _ in xrange(16)])
            value = ''.join([random.choice(string.hexdigits)
                           for _ in xrange(16)])
            t = t + random.randint(10, 100) * 10
            measurements[t] = {key:value, 'time': str(t)}
            store.set(sid, t, {key:value})
        return measurements   
