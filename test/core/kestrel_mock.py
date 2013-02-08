'''
Created on Jan 25, 2013

@author: cosmin
'''
import threading
import unittest

from nose.plugins.attrib import attr

from core import kestrel_mock

class KestrelMockTest(unittest.TestCase):

    def setUp(self):
        super(KestrelMockTest, self).setUp()
        self._queue_system = kestrel_mock.KestrelMock() 
        pass

    def tearDown(self):
        super(KestrelMockTest, self).tearDown()
        pass
    
    @attr('unit')
    def testOneQueue(self):
        queue1 = "test1"
        
        for i in range(1, 10):
            self._queue_system.add(queue1, str(i), None)
        
        for i in range(1, 10):
            j = int(self._queue_system.get(queue1, None))
            self.assertEqual(i, j, "it needs to be a fifo")    
    
    @attr('unit')
    def testTwoQueues(self):
        queue1 = "test1"
        queue2 = "test2"
        
        count = 10
        
        for i in range(1, count):
            self._queue_system.add(queue1, str(i), None)
            self._queue_system.add(queue2, str(count - i), None)
        
        for i in range(1, count):
            j = int(self._queue_system.get(queue1, None))
            self.assertEqual(i, j, "it needs to be a fifo")
            
            j = int(self._queue_system.get(queue2, None))
            self.assertEqual(count - i, j, "it needs to be a fifo")
    
    @attr('unit')
    def testGetTimeout(self):
        timeout = 1 
        queue1 = "test1"
        
        def get():
            item = self._queue_system.get(queue1, timeout)
            self.assertIsNone(item, "Should return None on timeout")
        
        worker = threading.Thread(target=get)
        worker.setDaemon(True)
        
        worker.start()
        worker.join(1.5 * timeout)
        self.assertFalse(worker.is_alive(), "Should have timedout")