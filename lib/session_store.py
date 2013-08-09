from collections import defaultdict
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

        # Fetch at most 2*N measurements for each session to try and find
        # at least N measurements that have the given keys. If we don't get
        # lucky, that's just too bad, it's too complicated to do it otherwise.
        return self.get_sessions_measurements(sessions, keys, 2*N, True)

    def get_sessions_times(self, session_ids):
        """ Given a set of session_ids, retrieve a dictionary mapping each
        session_id to its list of timestamps. """

        pipeline = self.redis.pipeline()
        for session_id in session_ids:
            pipeline.zrevrange('stimes:%s' % session_id, 0, -1)
        pipeline_results = pipeline.execute()
        return dict(zip(session_ids, pipeline_results))

    def get_sessions_measurements(self, session_ids, properties=[], N=100,
                                  ignore_if_missing=False):
        """ Given a set of session_ids, retrieve a dictionary mapping each
        session ids to a list of measurements.

        We also retrieve only a number of at most N measurements per session,
        out of practical reasons: there can be arbitrarily many measurements
        in a session, and the measurements we're looking for can be arbitrarily
        sparse. This would complicate getting all the measurements via a
        Redis pipeline, because getting a batch could potentially not be enough.

        """
        sessions_times = self.get_sessions_times(session_ids)
        pipeline = self.redis.pipeline()
        result_keys = []
        result = defaultdict(list)
        for session_id, times in sessions_times.iteritems():
            for t in times[:N]:
                result_keys.append((session_id, t))
                measurement_key = _hash_name(session_id, t)
                if not properties:
                    pipeline.hgetall(measurement_key)
                else:
                    pipeline.hmget(measurement_key, properties)
        pipeline_result = pipeline.execute()
        print "GOT %d results from Redis pipeline for %d sessions" % (len(pipeline_result), len(session_ids))
        for ((session_id, t), packed_measurement) in zip(result_keys, pipeline_result):
            if properties:
                packed_measurement = dict(zip(properties, packed_measurement))

            # Skip this measurement if we already have what we need for
            # the session_id in question.
            if N is not None and len(result[session_id]) >= N:
                continue

            measurement = _unpack_dict_values(packed_measurement)
            add_to_result = True

            # If we should ignore measurements who don't have all the
            # mentioned properties, check the current measurement - if it has
            # everything we need or not.
            if ignore_if_missing:
                for prop in properties:
                    if (prop not in measurement) or measurement[prop] is None:
                        add_to_result = False

            if add_to_result:
                result[session_id].append(measurement)
        return result

    def get_session_times(self, sid):
        """ Returns the list of times within a session, sorted descending. """
        return [int(x) for x in self.redis.zrevrange('stimes:%s' % sid, 0, -1)]

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
