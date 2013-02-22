import time

from mongoengine import connect

from core.experiment_file import ExperimentFile
from models.experiment import Experiment
from pdu import PDU

class RecordingPDU(PDU):
    '''
    A PDU that records data according to the defined experiments
    '''
    QUEUE = 'recorder'

    ''' Every FILES_PURGE_THRESHOLD seconds, check to see which experiments are
    no longer activated and close the open file associated with it'''
    FILES_PURGE_THRESHOLD = 5 * 60

    def __init__(self, **kwargs):
        super(RecordingPDU, self).__init__(**kwargs)
        self._last_files_purge = time.time()
        # dict of open files by experiment id
        self._open_files = {}
        connect('experiments')

    def process_message(self, message):
        # Purge open files once in a while
        current_time = time.time()
        if current_time - self._last_files_purge >= self.FILES_PURGE_THRESHOLD:
            self.purge_files()

        # Get active experiments matching this message
        experiments = Experiment.get_active_experiments_matching(message)
        experiment_ids = [str(e.id) for e in experiments]
        if len(experiment_ids) > 0:
            self.logger.info("Measurement %r matches experiments %r" %\
                             (self._json_dumps(message), experiment_ids))

        # Write the measurement to each experiment file
        for e in experiments:
            efile = self.get_file_for_experiment(e)
            efile.put(message)
            self.logger.info("Written measurement to file %s" % e.file)

    def get_file_for_experiment(self, e):
        ''' Lazily create and open a file for experiment'''
        efile = self._open_files.get(e.id)

        if efile is None:
            efile = ExperimentFile(e.file)
            efile.open_for_writing()
            self._open_files[e.id] = efile
            self.logger.info("Lazily opened file %s for writing for "
                             "experiment %r" % e.id)
        else:
            self.logger.info("File for experiment %r was already open" % e.id)

        return efile

    def purge_files(self):
        ''' Compare the list of active exercises with the list of open files to
        determine which are to be closed'''

        self.logger.info("Starting to purge files ...")

        active_ids = set([e.id for e in Experiment.get_active_experiments()])
        self.logger.info("Active experiment IDs: %r" % active_ids)

        open_files = {}
        for (ident, efile) in self._open_files.iteritems():
            if ident not in active_ids:
                efile.close()
                self.logger.info("Closing down file for experiment %s,"
                                 "because its experiment is no longer active" %\
                                 str(ident))
            else:
                open_files[ident] = efile

        self._open_files = open_files

if __name__ == '__main__':
    module = RecordingPDU()
    module.run()
