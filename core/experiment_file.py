import json
import os
import time

class ExperimentFile:
    ''' Utility class for writing messages for an experiment into a file
    It writes them as one json string per line. '''

    def __init__(self, fname):
        self.fname = fname
        self.last_access = time.time()

    def open_for_writing(self):
        self._file = open(self.fname, 'wt')

    def open_for_reading(self):
        self._file = open(self.fname, 'rt')
        for line in self._file:
            message = json.loads(line)
            yield message

    def put(self, message):
        self._last_access = time.time()
        json.dump(message, self._file)
        self._file.write(os.linesep)
        self._file.flush()

    def close(self):
        self._file.close()