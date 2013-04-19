import logging

import redis

from core import settings

logger = logging.getLogger(__name__)

class SessionsStore(object):
    def __init__(self):
        self.redis = redis.StrictRedis(host=settings.REDIS_SERVER,
                                             port=settings.REDIS_PORT,
                                             db=settings.REDIS_DASHBOARD_DB)
                

    def set(self, sid, time, prop, value):
        """
        Set the value of a property for the measurment sid/time.
        The 'time' property is added to the measurement automatically"
        """
        self.redis.sadd('sessions', sid)
        self.redis.sadd('stimes:' + sid, time)
        self.redis.hset(_hash_name(sid, time), prop, value);
        self.redis.hset('m:' + sid + ':' + str(time), 'time', time);
        
    
    def get_all_sessions(self):
        "Returns the list of all active sessions"
        return self.redis.smembers('sessions')

    def get_session_times(self, sid):
        return [int(x) for x in self.redis.smembers('stimes:' + sid)]
        
    def get_session_measurements(self, sid, properties = []):
        """
        Returns the values of the specified properties for all measurements of this session as list of dicts
        """
        times = self.redis.smembers('stimes:' + sid)
        ret = []
        for t in times:
            ret.append(self.get_session_measurement(sid, t, properties))
        
        return ret
        
    def get_session_measurement(self, sid, t, properties = []):
        "Returns the value of the specified properties of session at time t as a dict"
        if properties == []:
            return self.redis.hgetall(_hash_name(sid, t))
        else:
            values = self.redis.hmget(_hash_name(sid, t), properties)
            ret = {}
            for i in range(len(properties)):
                ret[properties[i]] = values[i]
            return ret
        
   
def _hash_name(sid, time):
    return 'm:' + sid + ':' + str(time)
    
        
        