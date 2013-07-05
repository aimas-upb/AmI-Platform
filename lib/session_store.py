import logging
import random
import time

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
    STALE_SESSION_THRESHOLD_MS = 60 * 60 * 1000 # 1 hour
    CLEANUP_PROBABILITY = 0.05 # 5% chance of cleaning up old sessions randomly
    MAX_SESSIONS_TO_CLEANUP = 100

    def __init__(self):
        self.redis = redis.StrictRedis(host=settings.REDIS_SERVER,
                                       port=settings.REDIS_PORT,
                                       db=settings.REDIS_SESSION_DB)

    def set(self, sid, timestamp, info):
        """
            Set the value of a property for the measurment sid/time.
            The 'time' property is added to the measurement automatically"
        """
        timestamp = _round_down(timestamp)
        self._update_session_max_timestamp(sid, timestamp)

        # stimes is a sorted set of timestamps for a given session
        self.redis.zadd('stimes:%s' % sid, timestamp, str(timestamp))
        info['time'] = timestamp
        self.redis.hmset(_hash_name(sid, timestamp), info)

        self._try_cleanup_some_stale_sessions()

    def get_all_sessions(self):
        """ Returns the list of all active sessions """
        return self.redis.hkeys('sessions')

    def get_all_sessions_with_last_update(self):
        """ Returns a dictionary containing session ids as keys and
        last update timestamps as values. """
        return dict((sid, int(timestamp))
                    for sid, timestamp in
                    self.redis.hgetall('sessions').iteritems())

    def get_session_times(self, sid):
        """ Returns the list of times within a session, sorted ascending. """
        return [int(x) for x in self.redis.zrevrange('stimes:%s' % sid, 0, -1)]

    def get_session_measurements(self, sid, properties = []):
        """ Returns the values of the specified properties for all
        measurements of this session as list of dicts. """
        return [self.get_session_measurement(sid, t, properties)
                for t in self.get_session_times(sid)]

    def remove_session(self, sid):
        """ Remove a session completely. """

        # Remove session_id -> last_updated_at mappings
        self.redis.hdel('sessions', sid)

        session_times = self.get_session_times(sid)

        # Remove list of sorted session timestamps
        self.redis.delete('stimes:%s' % sid)

        # Delete entries for each session timestamp
        keys = [_hash_name(sid, timestamp) for timestamp in session_times]
        self.redis.delete(*keys)

    def stale_sessions(self):
        """ Return the sessions which are stale (e.g. whose last_update) is
        less than STALE_SESSION_THRESHOLD miliseconds ago. """
        sessions = self.get_all_sessions_with_last_update()
        result = []
        threshold = int(time.time() * 1000) - self.STALE_SESSION_THRESHOLD_MS
        for session_id, last_updated_at in sessions.iteritems():
            if last_updated_at < threshold:
                result.append(session_id)
        return result

    def get_session_measurement(self, sid, t, properties = []):
        """ Returns the value of the specified properties of
        session at time t as a dict. """
        if not properties:
            return self.redis.hgetall(_hash_name(sid, t))
        else:
            values = self.redis.hmget(_hash_name(sid, t), properties)
            return dict(zip(properties, values))

    def _update_session_max_timestamp(self, sid, timestamp):
        # "sessions" is a session_id -> max(measurement_timestamp) mapping
        # that works like a hearbeat table, allowing us to clean-up old
        # sessions that are no longer needed
        max_timestamp = self.redis.hget('sessions', sid)
        if max_timestamp is None:
            new_timestamp = timestamp
        else:
            try:
                max_timestamp = int(max_timestamp)
                new_timestamp = max(timestamp, max_timestamp)
            except:
                # If we have crap in the session store, default to
                # having current timestamp as the new max
                new_timestamp = timestamp

        self.redis.hset('sessions', sid, new_timestamp)

    def _try_cleanup_some_stale_sessions(self):

        # With a probability of 5%, clean up 100 old sessions
        if random.random() > self.CLEANUP_PROBABILITY:
            return

        stale_sessions = self.stale_sessions()
        to_clean = min(len(stale_sessions), self.MAX_SESSIONS_TO_CLEANUP)
        random_stale_sessions = random.sample(stale_sessions, to_clean)
        for stale_session in random_stale_sessions:
            self.remove_session(stale_session)

def _round_down(time):
    return (time / 10) * 10

def _hash_name(sid, time):
    return 'm:' + sid + ':' + str(time)


