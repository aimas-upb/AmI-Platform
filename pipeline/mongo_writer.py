from collections import defaultdict
import time
import pymongo
from pymongo.errors import OperationFailure

from core import PDU
from core import constants

class MongoWriter(PDU):
	"""	PDU for writing all measurements to MongoDB. """

	QUEUE = 'mongo-writer'
	DATABASE = 'measurements'
	COLLECTION = 'docs'
	TTL = constants.SECONDS_IN_DAY
	BETWEEN_WRITES = 1 # seconds between writes for a sensor_type

	def __init__(self):
		""" After performing base class initializations, make sure that
			the mongo collection where measurements are written has a TTL
			index on the created_at column.
		"""
		super(MongoWriter, self).__init__()
		self.collection.ensure_index([('created_at', pymongo.DESCENDING)],
									 background = True,
									 expireAfterSeconds = self.TTL)
		self.collection.ensure_index('context');
		self.last_written_for_sensor_type = defaultdict(lambda: 0)

	def process_message(self, message):
		""" This PDU processes messages by writing them to MongoDB.

		Measurements are written to a predefined collection, which is a
		TTL collection that expires items older than 1 day. We need a TTL
		collection so that our database doesn't fill up.

		"""
		if not self._should_be_saved(message):
			return

		try:
			self.collection.save(message, safe = True)

			# After saving the message successfully, mark it as saved
			self._mark_as_saved(message)
		except OperationFailure, e:
			import traceback
			traceback.print_exc()

	@property
	def collection(self):
		""" Shortcut for getting the Mongo collection. """
		try:
			db = getattr(self.mongo_connection, self.DATABASE, None)
			collection = getattr(db, self.COLLECTION, None)
			return collection
		except:
			import traceback
			traceback.print_exc()
			return None

	def _should_be_saved(self, message):
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

if __name__ == "__main__":
	module = MongoWriter()
	module.run()
