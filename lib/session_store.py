import json
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
    STALE_SESSION_THRESHOLD_MS = 30 * 60 * 1000 # 30 minutes
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
        # expire wants input in seconds
        self.redis.expire('stimes:%s' % sid,
                          self.STALE_SESSION_THRESHOLD_MS / 1000)

        info['time'] = timestamp
        self.redis.hmset(_hash_name(sid, timestamp), _pack_dict_values(info))
        self.redis.expire(_hash_name(sid, timestamp),
                          self.STALE_SESSION_THRESHOLD_MS / 1000)

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

    def get_all_sessions_with_measurements(self,
                                           N=100,
                                           keys=['subject_position', 'time'],
                                           max_sessions=None):
        """ Retrieve all the sessions with their last N measurements which have
        keys specified as a parameter. If there are less than N measurements
        with this property, all of them will be returned.

        Also, returned measurements will be sorted decreasing by timestamp -
        first measurement will be most recent. We don't need to worry ourselves
        with returning stale sessions, because we have an automatic algorithm
        for that (see _try_cleanup_some_stale_sessions).
        """
        sessions = self.get_all_sessions()
        if max_sessions is not None:
            sessions = sessions[:max_sessions]
        return {sid: self.get_session_measurements(sid, keys, N, True)
                for sid in sessions}

    def get_session_times(self, sid):
        """ Returns the list of times within a session, sorted descending. """
        return [int(x) for x in self.redis.zrevrange('stimes:%s' % sid, 0, -1)]

    def get_session_measurements(self, sid, properties=[],
                                 N=None, ignore_if_missing=False):
        """ Returns the values of the specified properties for all
        measurements of this session as list of dicts. """

        result = []
        for t in self.get_session_times(sid):
            measurement = self.get_session_measurement(sid, t, properties)
            add_to_result = True

            # If we should ignore measurements who don't have all the
            # mentioned properties, check the current measurement - if it has
            # everything we need or not.
            if ignore_if_missing:
                for prop in properties:
                    if (prop not in measurement) or measurement[prop] is None:
                        add_to_result = False

            if add_to_result:
                result.append(measurement)

                # Make sure to limit the number of results if this is desired
                if (N is not None) and len(result) == N:
                    break

        return result

    def remove_session(self, sid):
        """ Remove a session completely. """

        # Remove session_id -> last_updated_at mappings.
        #
        # The rest is done automatically by using the native Redis expiry
        # mechanism. We tried to delete all the sessions here but it worked
        # poorly.
        self.redis.hdel('sessions', sid)

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
        return _unpack_dict_values(self._get_session_measurement(sid,
                                                                 t,
                                                                 properties))

    def _get_session_measurement(self, sid, t, properties = []):
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


def _unpack_dict_values(info):
    result = {}
    for k, v in info.iteritems():
        try:
            result[k] = json.loads(v)
        except:
            result[k] = v
    return result

def _pack_dict_values(info):
    result = {}
    for k, v in info.iteritems():
        result[k] = json.dumps(v)
    return result
