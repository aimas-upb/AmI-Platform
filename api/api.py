import json
import bottle
from bottle import route, run, request, abort
from pymongo import Connection
from core import settings

@route('/latest_kinect_rgb', method='GET')
def get_latest_kinect_rgb():
    connection = Connection(settings.MONGO_SERVER)
    db = connection.measurements.docs
    finddict = {
        'sensor_id': 0,
        'sensor_type': 'kinect',
        'type': 'image_rgb'
    }
    image = db.find(finddict, limit = 1).sort('created_at', -1)[0]
    del image['_id']
    return json.dumps(image)

@route('/latest_kinect_skeleton', method='GET')
def get_latest_kinect_skeleton():
    connection = Connection(settings.MONGO_SERVER)
    db = connection.measurements.docs
    finddict = {
        'sensor_id': 0,
        'sensor_type': 'kinect',
        'type': 'skeleton'
    }
    skeleton = db.find(finddict, limit = 1).sort('created_at', -1)[0]
    del skeleton['_id']
    return json.dumps(skeleton)

run(host='0.0.0.0', port=8000)