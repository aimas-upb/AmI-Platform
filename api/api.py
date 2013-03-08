import json
import logging

from bottle import route, run

from lib.dashboard_cache import DashboardCache
from lib.log import setup_logging

logger = logging.getLogger(__name__)
dashboard_cache = DashboardCache()

POSITIONS_LIMIT = 5

@route('/latest_kinect_rgb/:sensor_id', method='GET')
def get_latest_kinect_rgb(sensor_id = 'daq-01'):
    try:
        result = dashboard_cache.get(sensor_id=sensor_id,
                                     sensor_type='kinect',
                                     measurement_type='image_rgb')
        return json.loads(result)
    except:
        logger.exception("Failed to get latest kinect RGB from Redis")
        return {}

@route('/latest_kinect_skeleton/:sensor_id', method='GET')
def get_latest_kinect_skeleton(sensor_id = 'daq-01'):
    try:
        result = dashboard_cache.get(sensor_id=sensor_id,
                                     sensor_type='kinect',
                                     measurement_type='skeleton')
        return json.loads(result)
    except:
        logger.exception("Failed to get latest kinect skeleton from Redis")
        return {}

@route('/get_latest_subject_positions', method='GET')
def get_latest_subject_positions():
#    db = get_db()
#    finddict = {
#        'type': 'subject_position'
#    }
#    positions = list(db.find(finddict, limit = POSITIONS_LIMIT).sort(
#                                                            'created_at', -1))
#    for position in positions:
#        del position['_id']
#    return json.dumps(positions)
    return {}

setup_logging()
run(host='0.0.0.0', port=8000)
