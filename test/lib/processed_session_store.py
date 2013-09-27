import logging
import random
import time
from unittest import TestCase

import redis
from nose.tools import eq_

from core import settings
from lib import log
from lib.processed_session_store import ProcessedSessionStore


class ProcessedSessionStoreTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super(ProcessedSessionStoreTest, cls).setUpClass()
        # TODO(andrei): move this into a custom test runner
        log.setup_logging(level=logging.DEBUG)

    def setUp(self):
        super(ProcessedSessionStoreTest, self).setUp()
        settings.REDIS_SERVER = 'localhost'

        self.redis = redis.StrictRedis(host=settings.REDIS_SERVER,
                                       port=settings.REDIS_PORT,
                                       db=settings.REDIS_SESSION_DB)

        self.redis.flushdb()
        self.store = ProcessedSessionStore()

    def test_new_session_id_returns_different_every_time(self):
        """ Check that new_session_id() always returns different results. """
        N = random.randint(5, 10)
        session_ids = [self.store.new_session_id() for _ in xrange(N)]
        eq_(len(session_ids), len(set(session_ids)),
            "Generated session ids should all be different!")

    def _create_new_session(self, N=None,
                            min_t=None, max_t=None,
                            min_x=None, max_x=None,
                            min_y=None, max_y=None,
                            min_z=None, max_z=None):

        N = N or random.randint(50, 100)
        min_t = min_t or int(time.time()) - 10
        max_t = max_t or int(time.time())

        sid = self.store.new_session_id()

        for _ in xrange(N):
            t = random.randint(min_t, max_t)
            info = {}
            if min_x is not None and max_x is not None:
                info['X'] = random.uniform(min_x, max_x)
            if min_y is not None and max_y is not None:
                info['Y'] = random.uniform(min_y, max_y)
            if min_z is not None and max_z is not None:
                info['Z'] = random.uniform(min_z, max_z)
            self.store.set(sid, t, info)

        return sid

    def test_no_session_returned_if_all_are_stale(self):
        """ Given a new measurement, and a set of stale sessions,
        check that no session is returned for matching with our without
        position.

        NOTE: for positional matching we deliberately set the session
        coordinates equal to the ones of the measurement so that we
        ensure the check is done temporally and not spatially.

        """
        num_sessions = random.randint(10, 20)
        t = int(time.time() * 1000)
        threshold = ProcessedSessionStore.TIME_MATCHING_THRESHOLD_MS
        old_time_min = t - threshold - 20
        old_time_max = t - threshold - 10

        for _ in xrange(num_sessions):
            self._create_new_session(min_t=old_time_min, max_t=old_time_max)

        message = {'time': t,
                   'info': {'X': None, 'Y': None, 'Z': None},
                   'session_id': None}
        eq_(self.store.session_ending_at(message), None,
            "No stale session should be returned")

        # Add some sessions with positional matching
        X = random.uniform(100, 500)
        Y = random.uniform(100, 500)
        Z = random.uniform(100, 500)
        for _ in xrange(num_sessions):
            self._create_new_session(min_t=old_time_min, max_t=old_time_max,
                                     min_x=X, max_x=X,
                                     min_y=Y, max_y=Y,
                                     min_z=Z, max_z=Z)

        message = {'time': t,
                   'info': {'X': X, 'Y': Y, 'Z': Z},
                   'session_id': None}
        eq_(self.store.session_ending_at(message), None,
            "No stale session should be returned")

    def test_new_session_is_returned_with_temporal_match(self):

        num_sessions = random.randint(10, 20)
        t = int(time.time() * 1000)
        threshold = ProcessedSessionStore.TIME_MATCHING_THRESHOLD_MS
        old_time_min = t - threshold - 20
        old_time_max = t - threshold - 10

        for _ in xrange(num_sessions - 1):
            self._create_new_session(min_t=old_time_min, max_t=old_time_max)

        good_sid = self._create_new_session(min_t=t - threshold + 1,
                                            max_t=t)

        message = {'time': t,
                   'info': {'X': None, 'Y': None, 'Z': None},
                   'session_id': None}
        eq_(self.store.session_ending_at(message), good_sid,
            "The good session (having fresh updated_at) should be returned")

        X = random.uniform(100, 500)
        Y = random.uniform(100, 500)
        Z = random.uniform(100, 500)

        message = {'time': t,
                   'info': {'X': X, 'Y': Y, 'Z': Z},
                   'session_id': None}
        eq_(self.store.session_ending_at(message), None,
            "No session should be returned even if they are fresh because "
            "they have no positional data")

    def test_new_session_with_old_positional_data_is_not_returned(self):

        num_sessions = random.randint(10, 20)
        t = int(time.time() * 1000)
        threshold = ProcessedSessionStore.TIME_MATCHING_THRESHOLD_MS
        positional_threshold = ProcessedSessionStore.POSITION_MATCHING_THRESHOLD_MS
        old_time_min = t - threshold - 20
        old_time_max = t - threshold - 10

        for _ in xrange(num_sessions - 1):
            self._create_new_session(min_t=old_time_min, max_t=old_time_max)

        X = random.uniform(100, 500)
        Y = random.uniform(100, 500)
        Z = random.uniform(100, 500)

        # Create a "good" session. So far, it has no positional data.
        # We will add some "old" positional data, and see that it doesn't
        # get returned.
        good_sid = self._create_new_session(min_t=t - threshold + 1,
                                            max_t=t)
        N = random.randint(50, 100)
        for _ in xrange(N):
            old_timestamp = random.randint(t - positional_threshold - 20,
                                           t - positional_threshold - 10)
            self.store.set(good_sid, old_timestamp, {'X': X, 'Y': Y, 'Z': Z})

        message = {'time': t,
                   'info': {'X': X, 'Y': Y, 'Z': Z},
                   'session_id': None}
        eq_(self.store.session_ending_at(message), good_sid,
            "The good session (having fresh updated_at) should be returned")

        message = {'time': t,
                   'info': {'X': X, 'Y': Y, 'Z': Z},
                   'session_id': None}
        eq_(self.store.session_ending_at(message), None,
            "Good session should not be returned because it has old "
            "positional data")

    def test_new_session_with_fresh_but_far_positional_data_is_not_returned(self):

        num_sessions = random.randint(10, 20)
        t = int(time.time() * 1000)
        threshold = ProcessedSessionStore.TIME_MATCHING_THRESHOLD_MS
        positional_threshold = ProcessedSessionStore.POSITION_MATCHING_THRESHOLD_MS
        distance_threshold = ProcessedSessionStore.POSITION_MATCHING_THRESHOLD_MM
        old_time_min = t - threshold - 20
        old_time_max = t - threshold - 10

        for _ in xrange(num_sessions - 1):
            self._create_new_session(min_t=old_time_min, max_t=old_time_max)

        X = random.uniform(100, 500)
        Y = random.uniform(100, 500)
        Z = random.uniform(100, 500)

        # Create a "good" session. So far, it has no positional data.
        # We will add some "old" positional data, and see that it doesn't
        # get returned.
        good_sid = self._create_new_session(min_t=t - threshold + 1,
                                            max_t=t)
        N = random.randint(50, 100)
        for _ in xrange(N):
            new_timestamp = random.randint(t - positional_threshold + 1, t)
            info = {'X': X, 'Y': Y, 'Z': Z}
            coord = random.choice(info.keys())
            sign = random.choice([-1, 1])
            info[coord] += sign * (distance_threshold + random.uniform(0.5, 1))

            self.store.set(good_sid, new_timestamp, info)

        message = {'time': t,
                   'info': {'X': None, 'Y': None, 'Z': None},
                   'session_id': None}
        eq_(self.store.session_ending_at(message), good_sid,
            "The good session (having fresh updated_at) should be returned")

        message = {'time': t,
                   'info': {'X': X, 'Y': Y, 'Z': Z},
                   'session_id': None}
        eq_(self.store.session_ending_at(message), None,
            "Good session should not be returned because it has new but "
            "far away positional data")

    def test_new_session_with_fresh_and_near_positional_data_is_returned(self):

        num_sessions = random.randint(10, 20)
        t = int(time.time() * 1000)
        threshold = ProcessedSessionStore.TIME_MATCHING_THRESHOLD_MS
        positional_threshold = ProcessedSessionStore.POSITION_MATCHING_THRESHOLD_MS
        distance_threshold = ProcessedSessionStore.POSITION_MATCHING_THRESHOLD_MM
        old_time_min = t - threshold - 20
        old_time_max = t - threshold - 10

        for _ in xrange(num_sessions - 1):
            self._create_new_session(min_t=old_time_min, max_t=old_time_max)

        X = random.uniform(100, 500)
        Y = random.uniform(100, 500)
        Z = random.uniform(100, 500)

        # Create a "good" session. So far, it has no positional data.
        # We will add some "old" positional data, and see that it doesn't
        # get returned.
        good_sid = self._create_new_session(min_t=t - threshold + 1,
                                            max_t=t)
        N = random.randint(50, 100)
        for _ in xrange(N):
            new_timestamp = random.randint(t - positional_threshold + 1, t)
            info = {'X': X, 'Y': Y, 'Z': Z}
            coord = random.choice(info.keys())
            sign = random.choice([-1, 1])
            info[coord] += sign * (distance_threshold - random.uniform(0.5, 1))

            self.store.set(good_sid, new_timestamp, info)

        message = {'time': t,
                   'info': {'X': None, 'Y': None, 'Z': None},
                   'session_id': None}
        eq_(self.store.session_ending_at(message), good_sid,
            "The good session (having fresh updated_at) should be returned")

        message = {'time': t,
                   'info': {'X': X, 'Y': Y, 'Z': Z},
                   'session_id': None}
        eq_(self.store.session_ending_at(message), good_sid,
            "Good session should be returned because it has both new "
            "and near positional data")
