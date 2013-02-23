from bottle import route, run

from lib.dashboard_cache import DashboardCache

dashboard_cache = DashboardCache()

@route('/latest_kinect_rgb/:sensor_id', method='GET')
def get_latest_kinect_rgb(sensor_id = 'daq-01'):
    try:
        return dashboard_cache.get(sensor_id=sensor_id,
                                   sensor_type='kinect',
                                   measurement_type='image_rgb')
    except:
        return {}

@route('/latest_kinect_skeleton/:sensor_id', method='GET')
def get_latest_kinect_skeleton(sensor_id = 'daq-01'):
    try:
        return dashboard_cache.get(sensor_id=sensor_id,
                                   sensor_type='kinect',
                                   measurement_type='skeleton')
    except:
        return {}

run(host='0.0.0.0', port=8000)
