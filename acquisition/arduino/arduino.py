import requests
import arduino_conf
import logging
from lib.dashboard_cache import DashboardCache
from lib.log import setup_logging
import kestrel
import json
from itertools import chain

class Arduino_Acquisition(object):

	self.dashQueue = 'dashboard'

	def __init__(self):
		self.logger = logging.getLogger("__main__")
		self.dashboard = DashboardCache()
		self.data_queue = kestrel.Client(settings.KESTREL_SERVERS)
		
		
	def get_data(self,device):
		ip = device[0]
		device_id = device[1]
		r =requests.get("http://%s" %ip )
		if(r.status_code != requests.codes.ok):
			logger.error("IP %(ip)s returned request code %(code)s" %{'ip': ip, 'code': r.status_code})
		ard = r.json()
		ard['sensor_id'] = device_id
		measurements = list()
		for measurement in ard['data'].keys():
			message = {'sensor_type': ard['sensor_type'], \
						'sensor_id': ard['sensor_id'], \
						'measurement_type': measurement, \
						'measurement': ard['data'][measurement]}
			measurements.append(message)
		return measurements

	def gather_data(self):
		all_data = list()
		for ard in arduino_conf.devices:
			data = get_data(ard)
			all_data.append(data)
		final = list(chain.from_iterable(all_data))
		return final
	
	def send_message(self, msg):
		self.data_queue.add(self.dashQueue, json.dumps(msg))
		
	def send_data(self, data):
		logger.info("Sending data")
		for msg in data
			send_message(msg)
			
if __name__ == '__main__':
	setup_logging()
	module = Arduino_Acquisition()
	