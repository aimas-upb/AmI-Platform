from collections import OrderedDict
from datetime import datetime
import functools
import logging
import math
import random
import string
import time

import redis

from core import settings
from session_store import SessionStore

logger = logging.getLogger(__name__)

class ProcessedSessionStore(SessionStore):
    """
        Small layer over a Redis database holding processed session data.

        How this differs from normal session data:

            * session_ids are randomly generated (thus have no simple mapping
              backwards to the original session ids from the sensors)

            * measurements are written one by one and matched to the correct
              session which matches them "best".

        TODO(andrei):
            * make the algorithm for finding the best session "pluggable"
            * allow batch-level processing of trajectories (but I'm not sure
                yet how this plays with real-time processing)
    """

    TIME_MATCHING_THRESHOLD_MS = 500
    POSITION_MATCHING_THRESHOLD_MS = 5000
    POSITION_MATCHING_THRESHOLD_MM = 200

    def __init__(self):
        self.redis = redis.StrictRedis(host=settings.REDIS_SERVER,
                                       port=settings.REDIS_PORT,
                                       db=settings.REDIS_PROCESSED_SESSION_DB)

    def new_session_id(self):
        """
            Return a new random session id.

            New sessions are created whenever there is no session that matches
            an existing measurement close enough.
        """
        random_hash = ''.join([random.choice(string.hexdigits)
                               for _ in xrange(16)])
        return "%d_%s" % (int(time.time()), random_hash)

    def session_ending_at(self, t, info):
        """
            Given a (t, info) pair serving as a notification, get the
            best matching session which ends as close as possible to it.
            If there is no such session "close enough", returns None.
        """
        if self._has_position(info):
            return self._session_ending_at_with_position(t, info['X'],
                                                         info['Y'], info['Z'])
        else:
            return self._session_ending_at_without_position(t)

    def _has_position(self, info):
        """
            Return true iff a given measurement dict has room position about
            a sensor or not (X, Y, Z).
        """
        for key in ['X', 'Y', 'Z']:
            if key not in info:
                return False
            try:
                int(info[key])
            except:
                return False
        return True

    def _filtered_active_sessions_ordered_by_time(self, matcher=lambda x: True):
        """ Get the set of active sessions that match the matcher function,
        ordered descending by last updated time. """

        # TODO(andrei): use a max-heap, but the Python implementation is too
        # tangled to use it and I don't want to waste time implementing one now.

        # First step - filter the sessions by using the matcher function
        sessions = self.get_all_sessions_with_last_update()
        filtered_sessions = {}
        for sid, last_update in sessions.iteritems():
            if matcher(last_update):
                filtered_sessions[sid] = last_update

        # Second step - order the filtered sessions by last update decreasing
        result = filtered_sessions.items()
        result = sorted(result, key=lambda x:x[1], reverse=True)
        return OrderedDict(result)

    def _temporal_match(self, measurement_time, session_time):
        return abs(measurement_time - session_time) < \
               self.TIME_MATCHING_THRESHOLD_MS

    def _session_ending_at_without_position(self, t):
        """
            Return the closest session ending at time t, ignoring any other
            type of information (e.g. position).

            This is used whenever there is no position data (yet)
            for matching the measurement.
        """
        matcher = functools.partial(self._temporal_match, t)
        sessions = self._filtered_active_sessions_ordered_by_time(matcher=matcher)
        if len(sessions) == 0:
            logger.warn("No session found close enough to time %s" %
                        datetime.fromtimestamp(int(t / 1000.0)))
            return None

        # Return the most recently updated session id
        return sessions.iterkeys().next()

    def _has_recent_positional_match(self, sid, t, x, y, z):
        """ Given a session, determine whether it has a recent item in its
        timeline of measurements that has a position and which is geometrically
        close to our position. """

        # First, filter out only the "recent" session times.
        # In this case, the notion of "recent" is different from the one used
        # for filtering sessions - we have a higher standard for the updated
        # time of the session, and a lower standard for a position detected
        # within the session.
        session_times = self.get_session_times(sid)
        recent_session_times = []
        for session_time in session_times:
            if abs(session_time - t) < self.POSITION_MATCHING_THRESHOLD_MS:
                recent_session_times.append(session_time)

        for session_time in recent_session_times:
            # Get X, Y, Z for the measurement at time session_time, if
            # they are available
            measurement = self.get_session_measurement(sid,
                                                       session_time,
                                                       ['X', 'Y', 'Z'])

            # Skip the measurement if coordinates are not available for it
            if measurement['X'] is None or \
               measurement['Y'] is None or \
               measurement['Z'] is None:
                    continue

            # Redis client returns these values as strings
            X = float(measurement['X'])
            Y = float(measurement['Y'])
            Z = float(measurement['Z'])

            dist = math.sqrt((x - X) * (x - X) +
                             (y - Y) * (y - Y) +
                             (z - Z) * (z - Z))
            if dist < self.POSITION_MATCHING_THRESHOLD_MM:
                return True

        return False

    def _session_ending_at_with_position(self, t, x, y, z):

        # Get sessions that are "close enough" to our session temporally-wise
        matcher = functools.partial(self._temporal_match, t)
        sessions = self._filtered_active_sessions_ordered_by_time(matcher=matcher)
        if len(sessions) == 0:
            logger.warn("No session found close enough to time %s" %
                        datetime.fromtimestamp(int(t / 1000.0)))
            return None

        # Try each recently updated session, to see if the have a
        # "recent enough" position.
        for sid in sessions:
            if self._has_recent_positional_match(sid, t, x, y, z):
                return sid

        logger.warn("No session found close enough to time %s and coordinates "
                    "(%.2f, %.2f, %.2f)" %
                    (datetime.fromtimestamp(int(t / 1000.0)), x, y, z))
        return None
