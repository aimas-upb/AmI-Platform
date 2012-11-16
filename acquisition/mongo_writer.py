import time
import pymongo

from core import PDU
from core import constants

class MongoWriter(PDU):
	"""	PDU for writing all measurements to MongoDB. """

	QUEUE = 'mongo-writer'
	DATABASE = 'measurements'
	COLLECTION = 'docs'
	TTL = constants.SECONDS_IN_DAY

	def __init__(self):
		""" After performing base class initializations, make sure that
			the mongo collection where measurements are written has a TTL
			index on the created_at column.
		"""
		super(MongoWriter, self).__init__()
		self.collection.ensure_index([('created_at', pymongo.DESCENDING)],
									 background = True,
									 expireAfterSeconds = self.TTL)

	def process_message(self, message):
		""" This PDU processes messages by writing them to MongoDB.

		Measurements are written to a predefined collection, which is a
		TTL collection that expires items older than 1 day. We need a TTL
		collection so that our database doesn't fill up.

		"""
		# Add a created_at field so that
		message['created_at'] = int(time.time())
		self.collection.save(doc)

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

if __name__ == "__main__":
	module = MongoWriter()
	module.run()
