import json
import logging

from bottle import Bottle, run, static_file

from core import settings
from decorators import query_param
from lib.dashboard_cache import DashboardCache
from lib.log import setup_logging
from lib.session_store import SessionStore
from lib.processed_session_store import ProcessedSessionStore

logger = logging.getLogger(__name__)

app = Bottle()
dashboard_cache = DashboardCache()
session_store = SessionStore()
processed_session_store = ProcessedSessionStore()

POSITIONS_LIMIT = 100
ENVIRONMENT_LIMIT = 1000

if getattr(settings, 'SERVE_DASHBOARD_VIA_API', False):
    @app.route('/static/<filepath:path>')
    def static_serve(filepath):
        return static_file(filepath, root=getattr(settings, 'STATIC_FILES_DIR', '.'))

@app.route('/latest_kinect_rgb/:sensor_id', method='GET')
def get_latest_kinect_rgb(sensor_id = 'daq-01'):
    try:
        result = dashboard_cache.get(sensor_id=sensor_id,
                                     sensor_type='kinect',
                                     measurement_type='image_rgb')
        return json.loads(result)
    except:
        logger.exception("Failed to get latest kinect RGB from Redis")
        return {}

@app.route('/latest_kinect_skeleton/:sensor_id', method='GET')
def get_latest_kinect_skeleton(sensor_id = 'daq-01'):
    try:
        result = dashboard_cache.get(sensor_id=sensor_id,
                                     sensor_type='kinect',
                                     measurement_type='skeleton')
        return json.loads(result)
    except:
        logger.exception("Failed to get latest kinect skeleton from Redis")
        return {}

@app.route('/sessions/:session_type', method='GET')
@query_param('N', int, default=100)
@query_param('max_age', int, default=30)
def get_session_list(session_type, N, max_age):
    try:
        store = _get_session_store(session_type)
        return {'sessions': store.get_all_sessions_with_measurements(N=N,
                                                                     max_sessions=100,
                                                                     max_age=max_age)}
    except:
        logger.exception("Failed to get sessions from Redis")
        return {'sessions': {}}

@app.route('/latest_environment/:sensor_id', method='GET')
def get_latest_environment(sensor_id = 'K1-A'):
    try:
        result = dashboard_cache.lrange(sensor_id=sensor_id,
                                        sensor_type='arduino',
                                        measurement_type='environment',
                                        start=0,
                                        stop=ENVIRONMENT_LIMIT)
        return {'data': result}

    except:
        logger.exception("Failed to get list of latest environment data from "
                         "Redis")
        return {}

@app.route('/latest_subject_positions/:sensor_id', method='GET')
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

@app.route('/measurements/:session_type', method='GET')
@query_param('sid', str)
@query_param('time', int)
def get_measurement_properties(session_type, sid, time):
    store = _get_session_store(session_type)
    try:
        return {'measurements': store.get_session_measurement(sid, time)}
    except:
        return {'measurements': {}}
    pass

def _get_session_store(session_type):
    if session_type == 'raw':
        return session_store
    elif session_type == 'processed':
        return processed_session_store
    else:
        raise Exception("Invalid session type %s" % session_type)

if __name__ == '__main__':
    setup_logging()
    params = {
        'host': '0.0.0.0',
        'port': 8000
    }
    if getattr(settings, 'BOTTLE_BACKEND'):
        params['server'] = getattr(settings, 'BOTTLE_BACKEND')
    run(app, **params)
