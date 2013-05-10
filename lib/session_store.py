import logging

import redis

from core import settings

logger = logging.getLogger(__name__)

class SessionStore(object):
    """
        Small layer over a Redis database holding chronologically ordered
        tuples grouped by the session_id field.

        These tuples represent the activity of a user in relation to a sensor
        in time. We are assuming that the sensor is tracking the user through
        some means (for example, kinects track skeletons, and proximity sensors
        track distance to nearest object).

        Thus, each tuple will look like: (session_id, t, params), where
        params contains extra information about the session tracking at time t.
        For example, params can contain X,Y,Z of the actual user, or a picture.

        This is a data structure that we will use later on in order to aggregate
        information from multiple tracking sessions.
    """

    def __init__(self):
        self.redis = redis.StrictRedis(host=settings.REDIS_SERVER,
                                       port=settings.REDIS_PORT,
                                       db=settings.REDIS_SESSION_DB)

    def set(self, sid, time, info):
        """
            Set the value of a property for the measurment sid/time.
            The 'time' property is added to the measurement automatically"
        """
        time = _snap_time(time)
        # sessions is a set of session ids
        self.redis.hset('sessions', sid, time)
        # stimes is a sorted set of timestamps for a given session
        self.redis.zadd('stimes:%s' % sid, time, str(time))
        info['time'] = time
        self.redis.hmset(_hash_name(sid, time), info);

    def get_all_sessions(self):
        """ Returns the list of all active sessions """
        return self.redis.hkeys('sessions')

    def get_session_times(self, sid):
        """ Returns the list of times within a session, sorted ascending. """
        return [int(x) for x in self.redis.zrange('stimes:%s' % sid, 0, -1)]

    def get_session_measurements(self, sid, properties = []):
        """ Returns the values of the specified properties for all
        measurements of this session as list of dicts. """
        return [self.get_session_measurement(sid, t, properties)
                for t in self.get_session_times(sid)]

    def get_session_measurement(self, sid, t, properties = []):
        """ Returns the value of the specified properties of
        session at time t as a dict. """
        if not properties:
            return self.redis.hgetall(_hash_name(sid, t))
        else:
            values = self.redis.hmget(_hash_name(sid, t), properties)
            return dict(zip(properties, values))

def _snap_time(time):
    return (time / 10) * 10

def _hash_name(sid, time):
    return 'm:' + sid + ':' + str(time)


