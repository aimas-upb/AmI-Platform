'''
Created on Jan 25, 2013

@author: cosmin
'''

class KestrelMock(object):
    '''
    In-process mock implementation of kestrel.Client, especially useful for 
    running tests. 
    '''

    def __init__(self):
        '''
        Constructor
        '''
        pass

    def add(self, queue, data, expire=None):
        '''Add a job onto the queue.
            @see: kestrel.Client.add 
        '''
        
        pass
    
    def get(self, queue, timeout=None):
        '''Get a job off the queue. (unreliable)
        @see: kestrel.Client.add
        '''
        
        pass
    
    

