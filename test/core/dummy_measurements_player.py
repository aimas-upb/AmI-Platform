import json
import logging

logger = logging.getLogger(__name__)

class DummyMeasurementsPlayer(object):

    def __init__(self, data_file = None, callback = None, hardcoded_msgs = []):
        logger.info("Dummy Measurements player is alive!")
        logger.info("I will play back %d measurements." % len(hardcoded_msgs))
        self.callback = callback
        self.hardcoded_msgs = hardcoded_msgs

    def play(self):
        for msg in self.hardcoded_msgs:
            logger.info("Playing back harcoded message %r" % msg)
            self.callback(json.dumps(msg))