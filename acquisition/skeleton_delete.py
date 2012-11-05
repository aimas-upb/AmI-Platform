"""
	Given a set of MongoDB measurements, takes those related to kinect
	with a given context specified through command line (or otherwise
	all of them) and exports them to CSV9.
"""
import sys
import pymongo

DB_NAME = 'measurements'
COLLECTION_NAME = 'docs'

if __name__ == "__main__":
	context = "default" if len(sys.argv) == 1 else sys.argv[1]

	connection = pymongo.Connection()
	db = getattr(connection, DB_NAME)
	collection = getattr(db, COLLECTION_NAME)
	measurements = collection.remove({"context": context})
