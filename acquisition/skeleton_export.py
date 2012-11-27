"""
	Given a set of MongoDB measurements, takes those related to kinect
	with a given context specified through command line (or otherwise
	all of them) and exports them to CSV9.
"""
import sys
import pymongo

DB_NAME = 'measurements'
COLLECTION_NAME = 'docs'
POINTS = ["head", "neck", "left_shoulder", "right_shoulder",
	  "left_elbow", "right_elbow", "left_hand", "right_hand",
	  "torso", "left_hip", "right_hip", "left_knee", "right_knee",
          "left_foot", "right_foot"]

if __name__ == "__main__":
	context = "default" if len(sys.argv) == 1 else sys.argv[1]

	connection = pymongo.Connection()
	db = getattr(connection, DB_NAME)
	collection = getattr(db, COLLECTION_NAME)

	measurements = collection.find({"context": context, "sensor_type": "kinect"})
	if measurements.count() == 0:
		print "No measurements found for context %s" % context
		sys.exit()
	
	f = open("export-%s.csv" % context, "wt")
	header = ['%s_%s' % (point, axis) for point in POINTS for axis in ['x', 'y', 'z']]
	f.write(','.join(header) + '\n')

	for m in measurements:
		coords = [str(m['skeleton'][point][axis]) for point in POINTS for axis in ['X', 'Y', 'Z']]
		f.write(','.join(coords) + '\n')
		
	f.close()
