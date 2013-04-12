import requests
import arduino_conf
import logging
from lib.log import setup_logging
import kestrel
import json
from itertools import chain
from core import DAU
import os

class Arduino_Acquisition(DAU):

	QUEUE = 'dashboard'
	DATA_SAMPLING_FREQUENCY = int(os.environ["AMI_ARDUINO_SAMP_FREQ"]) #Needs to be in milliseconds
	
	def __init__(self, **kwargs):
		super(Arduino_Acquisition, self).__init__(**kwargs)
		
		
	def get_data(self,device):
		ip = device[0]
		device_id = device[1]
		r =requests.get("http://%s" %ip )
		if(r.status_code != requests.codes.ok):
			self.log("IP %(ip)s returned request code %(code)s" %{'ip': ip, 'code': r.status_code})
		ard = r.json()
		ard['sensor_id'] = device_id
		measurements = list()
		for measurement in ard['data'].keys():
			print ard['sensor_type'].upper()
			message = {'sensor_type': ard['sensor_type'].upper(), \
						'sensor_id': ard['sensor_id'], \
						'type': measurement.upper(), \
						'measurement': ard['data'][measurement]}
			measurements.append(message)
		return measurements

	def acquire_data(self):
		all_data = list()
		for ard in arduino_conf.devices:
			data = self.get_data(ard)
			all_data.append(data)
		final = list(chain.from_iterable(all_data))
		#print final
		return final
	
		
	
if __name__ == '__main__':
	setup_logging()
	module = Arduino_Acquisition()
	module.run()
