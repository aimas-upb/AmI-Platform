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

@route('/latest_subject_positions/:sensor_id', method='GET')
def get_latest_subject_positions(sensor_id = 'daq-01'):
    try:
        result = dashboard_cache.lrange(sensor_id=sensor_id,
                                        sensor_type='kinect',
                                        measurement_type='subject_position',
                                        start=0,
                                        stop=POSITIONS_LIMIT)
        return json.loads(result)
    except:
        logger.exception("Failed to get list of latest subject positions from "
                         "Redis")
        return {}

setup_logging()
run(host='0.0.0.0', port=8000)
