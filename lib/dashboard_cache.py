import logging

import redis

from core import settings

logger = logging.getLogger(__name__)

class DashboardCache(object):
    """ Cache which stores and retrieves images for dashboard usage. """

    def __init__(self):
        self.redis_cache = redis.StrictRedis(host=settings.REDIS_SERVER,
                                             port=settings.REDIS_PORT,
                                             db=settings.REDIS_DASHBOARD_DB)

    def put(self, sensor_id, sensor_type, measurement_type, measurement):
        key = self._redis_key(sensor_id, sensor_type, measurement_type)
        logger.info("Putting in redis at key %s" % key)
        self.redis_cache.set(key, measurement)

    def get(self, sensor_id, sensor_type, measurement_type):
        key = self._redis_key(sensor_id, sensor_type, measurement_type)
        logger.info("Getting from redis at key %s" % key)
        return self.redis_cache.get(key)

    def lpush(self, sensor_id, sensor_type, measurement_type, measurement):
        key = self._redis_key(sensor_id, sensor_type, measurement_type)
        logger.info("Pushing in redis at key %s" % key)
        self.redis_cache.lpush(key, measurement)
    
    def lrange(self, sensor_id, sensor_type, measurement_type, start, stop):
        key = self._redis_key(sensor_id, sensor_type, measurement_type)
        logger.info("Get list from redis at key %s" % key)
        return self.redis_cache.lrange(key, start, stop)

    def _redis_key(self, sensor_id, sensor_type, measurement_type):
        return '%s:%s:%s' % (sensor_id, sensor_type, measurement_type)
