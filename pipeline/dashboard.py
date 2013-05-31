import json

from core import PDU
from lib.dashboard_cache import DashboardCache
from lib.log import setup_logging
from lib.session_tracker import SessionTracker


class Dashboard(PDU):
    QUEUE = 'dashboard'

    def __init__(self, **kwargs):
        super(Dashboard, self).__init__(**kwargs)
        self.dashboard_cache = DashboardCache()
        self.session_tracker = SessionTracker()

    def process_message(self, message):
        push_to_redis = self.get_pushing_function(message)
        push_to_redis(sensor_id=message['sensor_id'],
                                 sensor_type=message['sensor_type'],
                                 measurement_type=message['type'],
                                 measurement=json.dumps(message))

        # Send the RGB image to SessionsStore only if the message has a
        # session_id. This means that, at kinect-level, there is an active
        # tracking session.
        if message['type'] == 'image_rgb' and message.get('session_id', None):
            sid = message['session_id']
            time = message['created_at']
            mappings = {'image_rgb': message['image_rgb']}
            self.session_tracker.track_event(sid, time, mappings)

    def get_pushing_function(self, message):
        if(message['sensor_type'] == "arduino"):
            return self.dashboard_cache.lpush
        else:
            return self.dashboard_cache.put

if __name__ == "__main__":
    setup_logging()
    module = Dashboard()
    module.run()
