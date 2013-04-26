import logging

import redis

from core import settings

logger = logging.getLogger(__name__)

class SessionsStore(object):
    """
        Small layer over a Redis databases holding chronologically ordered
        tuples groupbed by the session_id field.

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

    def __init__(self, db_name):
        self.redis = redis.StrictRedis(host=settings.REDIS_SERVER,
                                       port=settings.REDIS_PORT,
                                       db=db_name)

    def set(self, sid, time, mappings):
        """
            Set the value of a property for the measurment sid/time.
            The 'time' property is added to the measurement automatically"
        """
        time = _snap_time(time)
        self.redis.sadd('sessions', sid)
        self.redis.sadd('stimes:' + sid, time)
        mappings['time'] = time
        self.redis.hmset(_hash_name(sid, time), mappings);

    def get_all_sessions(self):
        """ Returns the list of all active sessions """
        return self.redis.smembers('sessions')

    def get_session_times(self, sid):
        """ Returns the list of times within a session. """
        return [int(x) for x in self.redis.smembers('stimes:' + sid)]

    def get_session_measurements(self, sid, properties = []):
        """ Returns the values of the specified properties for all
        measurements of this session as list of dicts. """
        times = self.redis.smembers('stimes:' + sid)
        ret = []
        for t in times:
            ret.append(self.get_session_measurement(sid, t, properties))

        return ret

    def get_session_measurement(self, sid, t, properties = []):
        """ Returns the value of the specified properties of
        session at time t as a dict. """
        if properties == []:
            return self.redis.hgetall(_hash_name(sid, t))
        else:
            values = self.redis.hmget(_hash_name(sid, t), properties)
            ret = {}
            for i in range(len(properties)):
                ret[properties[i]] = values[i]
            return ret

def _snap_time(time):
    return (time / 10) * 10

def _hash_name(sid, time):
    return 'm:' + sid + ':' + str(time)


