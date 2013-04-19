import logging
from unittest import TestCase

import redis
from nose.tools import eq_, ok_

from core import settings
from lib import log
from lib.sessions_store import SessionsStore

class SessionsStoreTest(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super(SessionsStoreTest, cls).setUpClass()
        log.setup_logging(level=logging.DEBUG)
        
    def setUp(self):
        super(SessionsStoreTest, self).setUp()
        settings.REDIS_SESSIONS_DB = 'sessions_store_test'
        settings.REDIS_SERVER = 'localhost'
        
        r = redis.StrictRedis(host = settings.REDIS_SERVER,
                              port = settings.REDIS_PORT,
                              db = settings.REDIS_SESSIONS_DB)
        
        r.flushdb()
        self.store = SessionsStore()
        
    def test_all(self):
        
        
        self.store.set('ts1', 1, 'p1', '1-1-p1')
        self.store.set('ts1', 2, 'p1', '1-2-p1')
        self.store.set('ts1', 1, 'p3', '1-1-p3')
        
        self.store.set('ts1', 3, 'p4', '1-3-p4')
        
        
        self.store.set('ts2', 2, 'p1', '2-2-p1')
        self.store.set('ts2', 2, 'p1', '2-2-p1-b')
        
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
        ok_(set([1,2,3]) == set(s1times), "Times must match")
        
        s2props = self.store.get_session_measurements('ts2', ['time'])
        s2times = [int(x['time']) for x in s2props]
        
        eq_(1, len(s2times), "Expecting 1 times")        
        ok_(set([2]) == set(s2times), "Times must match")
        
        
        
        
        
        
        
        
        
        
        
        
      
        
        
    