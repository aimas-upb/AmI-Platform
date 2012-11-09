import pymongo
import kestrel
import json
import time

QUEUE = 'measurements'
KESTREL_SERVERS = ['127.0.0.1:22133']
DB_NAME = 'measurements'
COLLECTION_NAME = 'docs'
DAYS = 1
SECONDS_IN_DAY = 24 * 60 * 60

kestrel_connection = kestrel.Client(KESTREL_SERVERS)
mongo_connection = pymongo.Connection()
db = getattr(mongo_connection, DB_NAME)
collection = getattr(db, COLLECTION_NAME)

collection.ensure_index([('created_at', pymongo.DESCENDING), 
			background = True,
			expireAfterSeconds = DAYS * SECONDS_IN_DAY) 

while True:
	try:
		# Step 1 - get message from kestrel queue
		message = kestrel_connection.get(QUEUE, timeout = 1)
		if not message:
			print "Could not get message. Retrying ..."
			continue
		
		# Step 2 - try to decode it assuming it's in correct
		# JSON format
		try:
			doc = json.loads(message)
		except:
			print "Did not get valid JSON from queue %s" % QUEUE
			print "Message = %s" % message
			import traceback
			traceback.print_exc()
			continue

		# Step 3.1 - put a created_at field on the message, so that
		# we can take advantage of Mongo's TTL collections and let
		# measurements older than DAYS days expire
		doc['created_at'] = int(time.time())

		# Step 3 - try to save to mongo
		try:
			collection.save(doc)
			print "Successfully saved message to mongo"
		except:
			print "Could not save document to mongo"
			print "doc = %r" % doc
			import traceback
			traceback.print_exc()
	except:
		print "Error while getting message from queue %s" % QUEUE
		import traceback
		traceback.print_exc()
