'''
Created on Jan 25, 2013

@author: cosmin
'''
import threading
import Queue

class KestrelMock(object):
    '''
    In-process mock implementation of kestrel.Client, especially useful for 
    running tests. 
    '''

    def __init__(self):
        self._queues = {}
        self._queues_lock = threading.Lock()
    
    def _get_queue(self, queue_name):
        self._queues_lock.acquire()
        try:
            queue = self._queues.get(queue_name)
            if queue is None:
                queue = Queue.Queue()
                self._queues[queue_name] = queue
            return queue
        finally:
            self._queues_lock.release()

    def add(self, queue_name, data, expire=None):
        '''Add a job onto the queue.
            @see: kestrel.Client.add 
        '''
        if expire is not None:
            raise Exception("Mock kestrel implementation does not support "
                            "expire")
         
        queue = self._get_queue(queue_name)
        queue.put(data, block=True)
        return True
    
    def get(self, queue_name, timeout=None):
        '''Get a job off the queue. (unreliable)
        @see: kestrel.Client.add
        '''

        queue = self._get_queue(queue_name)

        try:
            return queue.get(block=True, timeout=timeout)
        except Queue.Empty:
            return None
