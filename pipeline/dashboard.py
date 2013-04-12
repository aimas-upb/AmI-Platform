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
		push_to_redis = get_pushing_function(message)
		push_to_redis(sensor_id=message['sensor_id'],
                                 sensor_type=message['sensor_type'],
                                 measurement_type=message['type'],
                                 measurement=json.dumps(message))
								 
	def get_pushing_function(self, message):
		if(message['sensor_type'] == "arduino"):
			return self.dashboard_cache.lpush
		else:
			return self.dashboard_cache.put

if __name__ == "__main__":
    setup_logging()
    module = Dashboard()
    module.run()
