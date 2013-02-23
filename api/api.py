import json
import bottle
from bottle import route, run, request, abort
from pymongo import Connection
from core import settings

# Create indexes for mongo database
import pymongo
measurements = pymongo.Connection(settings.MONGO_SERVER).measurements.docs
measurements.ensure_index([('sensor_id', pymongo.ASCENDING),
                           ('sensor_type', pymongo.ASCENDING),
                           ('type', pymongo.ASCENDING),
                           ('created_at', pymongo.DESCENDING)])

@route('/latest_kinect_rgb/:sensor_id', method='GET')
def get_latest_kinect_rgb(sensor_id = 'daq-01'):
    connection = Connection(settings.MONGO_SERVER)
    db = connection.measurements.docs
    finddict = {
        'sensor_id': sensor_id,
        'sensor_type': 'kinect',
        'type': 'image_rgb'
    }
    images = list(db.find(finddict, limit = 1).sort('created_at', -1))
    if len(images) > 0:
        image = images[0]
        del image['_id']
        return json.dumps(image)
    else:
        return {}

@route('/latest_kinect_skeleton/:sensor_id', method='GET')
def get_latest_kinect_skeleton(sensor_id = 'daq-01'):
    connection = Connection(settings.MONGO_SERVER)
    db = connection.measurements.docs
    finddict = {
        'sensor_id': sensor_id,
        'sensor_type': 'kinect',
        'type': 'skeleton'
    }
    skeletons = list(db.find(finddict, limit = 1).sort('created_at', -1))
    if len(skeletons) > 0:
        skeleton = skeletons[0]
        del skeleton['_id']
        return json.dumps(skeleton)
    else:
        return {}

run(host='0.0.0.0', port=8000)
