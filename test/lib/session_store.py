import logging
import random
import string
import time
from unittest import TestCase

from mock import patch
from nose.tools import eq_, ok_
import redis

from core import settings
from lib import log
from lib.session_store import SessionStore

class SessionsStoreTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super(SessionsStoreTest, cls).setUpClass()
        # TODO(andrei): move this into a custom test runner
        log.setup_logging(level=logging.DEBUG)

    def setUp(self):
        super(SessionsStoreTest, self).setUp()
        settings.REDIS_SERVER = 'localhost'


        self.redis = redis.StrictRedis(host = settings.REDIS_SERVER,
                                       port = settings.REDIS_PORT,
                                       db = settings.REDIS_SESSION_DB)

        self.redis.flushdb()

        SessionStore.CLEANUP_PROBABILITY = 0
        self.store = SessionStore()

    def test_all(self):
        self.store.set('ts1', 30, {'p4': '1-3-p4'})

        self.store.set('ts1', 10, {'p1': '1-1-p1'})
        self.store.set('ts1', 20, {'p1': '1-2-p1'})
        self.store.set('ts1', 10, {'p3': '1-1-p3'})

        self.store.set('ts2', 20, {'p1': '2-2-p1'})
        self.store.set('ts2', 20, {'p1': '2-2-p1-b'})

        sessions = self.store.get_all_sessions()

        #test for the number of sessions
        eq_(2, len(sessions), "Expecting two sessions")
        ok_(set(sessions) == set(['ts1', 'ts2']), "Sessions must match")

        #test to see if
        s1props = self.store.get_session_measurements('ts1', ['p1'])
        s1p1 = [x['p1'] for x in s1props if x['p1'] is not None]
        ok_(set(['1-1-p1', '1-2-p1']) == set(s1p1), "Props must match")

        s1times = self.store.get_session_times('ts1')
        eq_(3, len(s1times), "Expecting 3 times")
        eq_([30,20,10], s1times, "Times must match")

        s2props = self.store.get_session_measurements('ts2', ['time'])
        s2times = [int(x['time']) for x in s2props]

        eq_(1, len(s2times), "Expecting 1 times")
        ok_(set([20]) == set(s2times), "Times must match")
        
    def test_keeps_type(self):
        self.store.set("session1", 30, {'p': {'x':1, 'y':{1:2}, 'z':[1,2,3]}})
        m = self.store.get_session_measurement("session1", 30, 'p')
        value = m['p']
        eq_(type(value), dict, "Expected dict")
        eq_(set(value.keys()), set(['x','y','z']))
        eq_(1, value['x'])
        eq_([1,2,3], value['z'])        

    def test_session_store_always_keeps_max_timestamp_for_measurements(self):
        """ Given that measurements may come in async with timestamps a little
        'out of order' because of that, test that no matter what happens, the
        session store will store only the max timestamp for each session. """

        self.store.set('session1', 200, {'a': 'b'})
        self.store.set('session1', 10, {'c': 'd'})

        last_timestamp = int(self.redis.hget('sessions', 'session1') or 0)
        eq_(last_timestamp, 200, "Session processor should always keep the "
            "maximal timestamp for out-of-order measurements")

    def test_stale_sessions_works_correctly(self):
        """ Check that detecting stale sessions works correctly. """
        result = self._create_mixture_of_fresh_and_stale_sessions()
        the_sessions = self.store.stale_sessions()
        eq_(set(the_sessions),
            set(result['stale']),
            "Stale sessions should be detected correctly.")

    def test_remove_session_works_correctly(self):
        """ Check that removing a session works correctly. """
        result = self._create_mixture_of_fresh_and_stale_sessions()
        sid = random.choice(result['stale'])
        self.store.remove_session(sid)

        # Check that there are no keys left for that session
        eq_(len(self.redis.keys('*%s*' % sid)), 0,
            "There should be no key containing the sid!")

        # Check that the session doesn't appear anymore in the
        # sid -> last_updated_at mapping
        sessions_updated_at = self.store.get_all_sessions_with_last_update()
        ok_(sid not in sessions_updated_at,
            "Removed session should not be present in mapping from sid to "
            "last updated at")

    def test_set_randomly_deletes_stale_sessions(self):
        """ Test that calling set() on the store should clean-up stale
        sessions correctly. """

        result = self._create_mixture_of_fresh_and_stale_sessions()
        stale_sids = result['stale']
        fresh_sid = random.choice(result['fresh'])

        # Small enough probability so that clean-up is triggered
        SessionStore.CLEANUP_PROBABILITY = 0.05        
        p = max(SessionStore.CLEANUP_PROBABILITY - 0.01, 0)
        with patch('random.random', return_value=p) as random_mock:
            with patch.object(SessionStore, 'remove_session') as remove_session_mock:
                # Perform a set() which will trigger a cleanup of stale sessions
                self.store.set(fresh_sid, int(time.time() * 1000), {})

                # First, check that remove session has been called with the
                # correct number of arguments.
                eq_(remove_session_mock.call_count,
                    len(stale_sids),
                    "Remove session should have been called the correct "
                    "number of times")

                # Next, let's check that the actual sessions on which
                # removeSession was called were the correct ones.
                removed_sids = []
                for remove_session_args in remove_session_mock.call_args_list:
                    removed_sids.append(remove_session_args[0][0])

                eq_(set(removed_sids), set(stale_sids),
                    "All stale sessions should have been removed")


    @patch('random.random', return_value=SessionStore.CLEANUP_PROBABILITY + 0.1)
    # We need to patch random.random() so that SessionStore.set() does
    # not perform any clean-up while creating the initial db contents.
    def _create_mixture_of_fresh_and_stale_sessions(self, random_patch):
        """ Creates a mixture of fresh and stale sessions.

        Returns a dictionary with two keys, one with the fresh session ids,
        and one with the stale session ids.

        """
        old_time = int(time.time() * 1000) - \
                   SessionStore.STALE_SESSION_THRESHOLD_MS

        result = {'fresh': [], 'stale': []}

        # We make sure to create less than MAX_SESSIONS_TO_CLEANUP
        # sessions because this way they will all be cleaned up on a
        # set() whose random factor is "good enough".
        N = SessionStore.MAX_SESSIONS_TO_CLEANUP
        n_fresh = random.randint(int(0.5 * N), N)
        n_stale = random.randint(int(0.5 * N), N)

        for _ in xrange(n_fresh):
            sid = ''.join([random.choice(string.hexdigits)
                           for _ in xrange(16)])
            result['stale'].append(sid)
            self.store.set(sid, old_time - random.randint(5000, 10000), {})

        for _ in xrange(n_stale):
            sid = ''.join([random.choice(string.hexdigits)
                           for _ in xrange(16)])
            result['fresh'].append(sid)
            self.store.set(sid, int(time.time() * 1000), {})

        return result
