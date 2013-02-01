import json
import os
import time

class ExperimentFile:
    ''' Utility class for writing messages for an experiment into a file
    It writes them as one json string per line. '''
    
    def __init__(self, fname):
        self.fname = fname
        self.last_access = time.time()
    
    def open(self):
        self._file = open(self.fname, 'w')
    
    def put(self, message):
        self._last_access = time.time()
        json.dump(message, self._file)
        self._file.write(os.linesep)
        self._file.flush()
        
    def close(self):
        self._file.close()