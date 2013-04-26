import json

from lib.dashboard_cache import DashboardCache
from lib.log import setup_logging
from pipeline.ami_lab_pdu import AmILabPDU

class Dashboard(AmILabPDU):
    QUEUE = 'dashboard'

    def __init__(self, **kwargs):
        super(Dashboard, self).__init__(**kwargs)
        self.dashboard_cache = DashboardCache()

    def process_message(self, message):
        push_to_redis = self.get_pushing_function(message)
        push_to_redis(sensor_id=message['sensor_id'],
                                 sensor_type=message['sensor_type'],
                                 measurement_type=message['type'],
                                 measurement=json.dumps(message))

        # Send the RGB image to SessionsStore only if the message has a
        # session_id. This means that, at kinect-level, there is an active
        # tracking session.
        if message.get('session_id', None):
            sid = message['session_id']
            time = message['created_at']
            self.add_to_session_store(sid, time, None)

    def get_pushing_function(self, message):
        if(message['sensor_type'] == "arduino"):
            return self.dashboard_cache.lpush
        else:
            return self.dashboard_cache.put

if __name__ == "__main__":
    setup_logging()
    module = Dashboard()
    module.run()
