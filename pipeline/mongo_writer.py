from collections import defaultdict
from datetime import datetime
import time
import pymongo
from pymongo.errors import OperationFailure

from core import PDU
from core import constants
from lib.log import setup_logging

class MongoWriter(PDU):
    """ PDU for writing all measurements to MongoDB. """

    QUEUE = 'mongo-writer'
    DATABASE = 'measurements'
    COLLECTION = 'docs'
    TTL = constants.SECONDS_IN_DAY
    BETWEEN_WRITES = 1 # seconds between writes for a sensor_type

    def __init__(self):
        """ After performing base class initializations, make sure that
            the mongo collection where measurements are written has a TTL
            index on the inserted_at column.
        """
        super(MongoWriter, self).__init__()
        # This index make sure that we only keep records in the measurements
        # db for a single day. We do this in order to avoid filling it.
        self.collection.ensure_index([('inserted_at', pymongo.DESCENDING)],
                                     background = True,
                                     expireAfterSeconds = self.TTL)

        # Most common type of query will be to get the measurements of
        # a given type from a given sensor.
        self.collection.ensure_index([('sensor_id', pymongo.ASCENDING),
                                      ('type', pymongo.ASCENDING)])
        self.collection.ensure_index('sensor_id')
        self.collection.ensure_index('type')

        self.last_written_for_sensor_type = defaultdict(lambda: 0)

    def process_message(self, message):
        """ This PDU processes messages by writing them to MongoDB.

        Measurements are written to a predefined collection, which is a
        TTL collection that expires items older than 1 day. We need a TTL
        collection so that our database doesn't fill up.

        """
        if not self._should_be_saved(message):
            self.log("Message has been rate-limited due to its sensor type: %s"\
                     % message['sensor_type'])
            return

        try:
            # Be careful to provide Mongo with the field in the format
            # required by the TTL collections feature. If we save this
            # as a plain unix timestamp, it won't get used correctly.
            message['inserted_at'] = datetime.now()
            self.collection.save(message, safe = True)

            # After saving the message successfully, mark it as saved
            self._mark_as_saved(message)
        except OperationFailure:
            self.logger.exception("Failed to save measurement to Mongo")

    @property
    def collection(self):
        """ Shortcut for getting the Mongo collection. """
        try:
            db = getattr(self.mongo_connection, self.DATABASE, None)
            collection = getattr(db, self.COLLECTION, None)
            return collection
        except:
            self.logger.exception("Could not get Mongo collection %s.%s" %\
                                  (self.DATABASE, self.COLLECTION))
            import traceback
            traceback.print_exc()
            return None

    def _should_be_saved(self, message):
        return True
        """ Decide whether the current message should be written or not.

        The decision is mased based on the last time a write was performed
        for that given sensor type.
        """
        # Messages that don't have a sensor_type will be rate-limited together
        sensor_type = message.get('sensor_type', 'default')

        last_written = self.last_written_for_sensor_type[sensor_type]
        return time.time() - last_written >= self.BETWEEN_WRITES

    def _mark_as_saved(self, message):
        """ Mark a message as successfully saved in the db.

        This actually updates the timestamp for the sensor_type of the message.
        """
        sensor_type = message.get('sensor_type', 'default')
        self.last_written_for_sensor_type[sensor_type] = time.time()
        self.log("Updated last_saved for sensor type %s -> %r" % (sensor_type,
                                                                  self.last_written_for_sensor_type))

if __name__ == "__main__":
    setup_logging()
    module = MongoWriter()
    module.run()
