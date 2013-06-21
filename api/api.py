import json
import logging

from bottle import route, run, static_file

from decorators import query_param
from core import settings
from lib.dashboard_cache import DashboardCache
from lib.log import setup_logging
from lib.session_store import SessionStore

logger = logging.getLogger(__name__)
dashboard_cache = DashboardCache()
session_store = SessionStore()

POSITIONS_LIMIT = 100

if getattr(settings, 'SERVE_DASHBOARD_VIA_API', False):
    @route('/static/<filepath:path>')
    def static_serve(filepath):
        return static_file(filepath, root=getattr(settings, 'STATIC_FILES_DIR', '.'))

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

@route('/session_list', method='GET')
@query_param('start', int, default = 0)
@query_param('end', int, default = None)
def get_session_list(start, end):
    try:
        sessions = session_store.get_all_sessions();
        return {'sessions': sessions[start:end]}    
    except:
        logger.exception("Failed to get sessions from Redis")
        return {}

@route('/latest_subject_positions/:sensor_id', method='GET')
def get_latest_subject_positions(sensor_id = 'daq-01'):
    try:
        result = dashboard_cache.lrange(sensor_id=sensor_id,
                                        sensor_type='kinect',
                                        measurement_type='subject_position',
                                        start=0,
                                        stop=POSITIONS_LIMIT)
        dashboard_cache.ltrim(sensor_id=sensor_id,
                              sensor_type='kinect',
                              measurement_type='subject_position',
                              start=0,
                              stop=POSITIONS_LIMIT)
        return {'data': result}

    except:
        logger.exception("Failed to get list of latest subject positions from "
                         "Redis")
        return {}


setup_logging()
run(host='0.0.0.0', port=8000)
