import json
import logging

from bottle import route, run

from lib.dashboard_cache import DashboardCache
from lib.log import setup_logging

logger = logging.getLogger(__name__)
dashboard_cache = DashboardCache()

POSITIONS_LIMIT = 100
ARDUINO_DATA_LIMIT = 50

ARDUINO_MEASUREMENTS = ["temperature", "luminosity", "sharp_data"]

@route('/latest_kinect_rgb/<sensor_id>', method='GET')
def get_latest_kinect_rgb(sensor_id = 'daq-01'):
    try:
        result = dashboard_cache.get(sensor_id=sensor_id,
                                     sensor_type='kinect',
                                     measurement_type='image_rgb')
        return json.loads(result)
    except:
        logger.exception("Failed to get latest kinect RGB from Redis")
        return {}

@route('/latest_kinect_skeleton/<sensor_id>', method='GET')
def get_latest_kinect_skeleton(sensor_id = 'daq-01'):
    try:
        result = dashboard_cache.get(sensor_id=sensor_id,
                                     sensor_type='kinect',
                                     measurement_type='skeleton')
        return json.loads(result)
    except:
        logger.exception("Failed to get latest kinect skeleton from Redis")
        return {}

@route('/latest_subject_positions/<sensor_id>', method='GET')
def get_latest_subject_positions(sensor_id = 'daq-01'):
    try:
        result = dashboard_cache.lrange(sensor_id=sensor_id,
                                        sensor_type='kinect',
                                        measurement_type='subject_position',
                                        start=0,
                                        stop=POSITIONS_LIMIT)
        return {'data': result}
    except:
        logger.exception("Failed to get list of latest subject positions from "
                         "Redis")
        return {}

@route('/latest_arduino_measurements/<sensor_id>/<measurement_type>', method='GET')
def get_latest_arduino_measurements(sensor_id, measurement_type):
	""" Will return last ARDUINO_DATA_LIMIT values for selected measurement. """
	try:
		result = dashboard_cache.lrange(sensor_id = sensor_id,
										sensor_type = 'arduino'
										measurement_type = measurement_type,
										start = 0,
										stop = ARDUINO_DATA_LIMIT)
		return {'data': result}
	except:
		logger.exception("Failed to get list of latest Arduino %s data from "
                         "Redis" % measurement_type)
        return {}
		
@route('/last_arduino_measurement/<sensor_id>/measurement_type>', method = 'GET')
def get_last_arduino_measurement(sensor_id, measurement_type):
	""" Will return last measurement value by using LIndex method. 
		Return value is a dictionary containing """
	try:
		result = dashboard_cache.lindex(sensor_id = sensor_id,
										sensor_type = 'arduino'
										measurement_type = measurement_type,
										index = 0)
		return json.loads(result)
	except:
		logger.exception("Failed to get latest Arduino %s data from "
                         "Redis" % measurement_type)
        return {}
		
@route('/latest_arduino_data/<sensor_id>', method= 'GET')
def get_last_arduino_data(sensor_id):
	try:
		lst = {}
		for measurement in ARDUINO_MEASUREMENTS:
			lst[measurement] = get_last_arduino_measurement(sensor_id, measurement)
		return lst
	except:
		logger.exception("Failed to get last data from Arduino id = %s" % sensor_id)
		return {}
		
setup_logging()
run(host='0.0.0.0', port=8000)
