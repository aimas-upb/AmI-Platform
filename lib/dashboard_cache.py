import redis

from core import settings

class DashboardCache(object):
    """ Cache which stores and retrieves images for dashboard usage. """

    def __init__(self):
        self.redis_cache = redis.StrictRedis(host=settings.REDIS_SERVER,
                                             port=settings.REDIS_PORT,
                                             db=settings.REDIS_DASHBOARD_DB)

    def put(self, sensor_id, sensor_type, measurement_type, measurement):
        key = self._redis_key(sensor_id, sensor_type, measurement_type)
        self.redis_cache.set(key, measurement)

    def get(self, sensor_id, sensor_type, measurement_type):
        key = self._redis_key(sensor_id, sensor_type, measurement_type)
        return self.redis_cache.get(key)

    def _redis_key(self, sensor_id, sensor_type, measurement_type):
        return '%s:%s:%s' % (sensor_id, sensor_type, measurement_type)
