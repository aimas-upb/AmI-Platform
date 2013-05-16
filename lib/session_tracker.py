import logging

from core import settings
from core.kestrel_connection import KestrelConnection
from lib.session_store import SessionStore

logger = logging.getLogger(__name__)


class SessionTracker(object):

    def __init__(self):
        self.session_store = SessionStore()
        self.kestrel_connection = KestrelConnection()

    def track_event(self, sid, time, info):
        message = {
            "session_id": sid,
            "time": time,
            "info": info,
        }

        self.kestrel_connection.send_to("session_processor", message)
        self.session_store.set(sid, time, info)
        logger.info("Track session:%s, time:%s, info: %s in Redis." %
                    (sid, time, info.keys()))
