import json

from core import PDU
from lib.dashboard_cache import DashboardCache
from lib.log import setup_logging

class Dashboard(PDU):
    QUEUE = 'dashboard'

    def __init__(self, **kwargs):
        super(Dashboard, self).__init__(**kwargs)
        self.dashboard_cache = DashboardCache()

    def process_message(self, message):
        self.dashboard_cache.put(sensor_id=message['sensor_id'],
                                 sensor_type=message['sensor_type'],
                                 measurement_type=message['type'],
                                 measurement=json.dumps(message))

if __name__ == "__main__":
    setup_logging()
    module = Dashboard()
    module.run()
