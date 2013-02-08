from models.experiment import Experiment
from pdu import PDU
from core.experiment_file import ExperimentFile
import time

class RecordingPDU(PDU):
    '''
    A PDU that records data according to the defined experiments
    '''

    ''' Every FILES_PURGE_THRESHOLD seconds, check to see which experiments are
    no longer activated and close the open file associated with it'''

    FILES_PURGE_THRESHOLD = 5 * 60

    def __init__(self, **kwargs):
        super(RecordingPDU, self).__init__(**kwargs)
        self._last_files_purge = time.time()
        '''dict of open files by experiment id'''
        self._open_files = {}

    def process_message(self, message):

        current_time = time.time()
        if current_time - self._last_files_purge >= self.FILES_PURGE_THRESHOLD:
            self.purge_files()

        for e in Experiment.get_active_experiments_matching(message):
            if e.active:
                efile = self.get_file_for_experiment(e)
                efile.put(message)

    def get_file_for_experiment(self, e):
        ''' Lazily create and open a file for experiment'''
        efile = self._open_files.get(e.id)
        if efile is None:
            efile = ExperimentFile(e.file)
            efile.open_for_writing()
            self._open_files[e.id] = efile

        return efile

    def purge_files(self):
        ''' Compare the list of active exercises with the list of open files to
        determint which are to be closed'''
        active_ids = set()
        for e in Experiment.get_active_experiments():
            active_ids.add(e.id)

        open_files = {}
        for (ident, efile) in self._open_files.iteritems():
            if ident not in active_ids:
                efile.close()
            else:
                open_files[ident] = efile

        self._open_files = open_files

