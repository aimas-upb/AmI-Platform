import logging
import json
import time

logger = logging.getLogger(__name__)

from core.experiment_file import ExperimentFile


class MeasurementsPlayer(object):

    def __init__(self, data_file, callback):
        self.data_file = data_file
        self.callback = callback
        self.experiment_file = ExperimentFile(self.data_file)

    def play(self):
        playback_start = int(time.time())
        measurement_start = None

        logger.info('Start replaying file')
        nb_messages = 0
        for measurement in self.experiment_file.open_for_reading():
            if not measurement_start:
                measurement_start = measurement['created_at']

            logger.info('Sending a message %s', measurement['sensor_id'])
            nb_messages += 1
            playback_delta = int(time.time()) - playback_start
            measurement_delta = measurement['created_at'] - measurement_start

            if playback_delta < measurement_delta:
                # Sleep in order to wait for the correct time to play
                # back this measurement.
                sleep_time = (measurement_delta - playback_delta) / 1000000.0
                logger.info('sleeping %r', sleep_time)
                time.sleep(sleep_time)

            self.callback(json.dumps(measurement))

        logger.info('Done replaying file with %s messages', nb_messages)

        self.experiment_file.close()
