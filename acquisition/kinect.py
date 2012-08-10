'''
	This script should be ran continuously in order to extract
	images from the Kinect using PyOpenNI python wrapper for
	OpenNI and put them on a kestrel queue.
'''

from openni import *
import kestrel
import pickle

kestrel_client = kestrel.Client(['127.0.0.1:22133'])
ctx = Context()
ctx.init()
depth = DepthGenerator()
depth.create(ctx)
ctx.start_generating_all()

for i in range(0, 100):
	ctx.wait_one_update_all(depth)
	depth_map = depth.get_tuple_depth_map()
	pickled_depth_map = pickle.dumps(depth_map)
	kestrel_client.add('ami53', pickled_depth_map)

kestrel_client.close()
