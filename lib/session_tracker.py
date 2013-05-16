import logging

from core import settings
from core.kestrel_connection import KestrelConnection
from lib.sessions_store import SessionsStore

logger = logging.getLogger(__name__)


class SessionTracker(object):

    def __init__(self):
        self.sessions_store = SessionsStore(settings.REDIS_RAW_SESSIONS_DB)
        self.kestrel_connection = KestrelConnection()

    def track_event(self, sid, time, info):
        message = {
            "session_id": sid,
            "time": time,
            "info": info,
        }

        self.kestrel_connection.send_to("session-processor", message)
        self.sessions_store.set(sid, time, info)
        logger.info("Track session:%s, time:%s, info: %s in Redis." %
                    (sid, time, info.keys()))
