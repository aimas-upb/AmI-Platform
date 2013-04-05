import json
import logging
import pymongo
import kestrel
import settings
import time
"""
	Data Acquisition Unit for Ami-Lab framework
	Its architecture resembles the design of PDU Class.
"""

class DAU(object):
	DATA_SAMPLING_FREQUENCY = 500 #miliseconds
	
	def __init__(self, **kwargs):
		self._mongo_connection = pymongo.Connection(settings.MONGO_SERVER)
		self.logger = logging.getLogger(self.__module__)
		self._output_queue = kwargs.get('queue_system', None) or kestrel.Client(settings.KESTREL_SERVERS)
		self._running = False
		
	def log(self, message, level = logging.INFO):
		self.logger.log(level, message)
		
	@property	
	def mongo_connection(self):
		return self._mongo_connection
		
	@property
	def output_queue_system(self):
		return self._output_queue
		
	def send_to(self, queue, message):
		""" Send a message to another queue. """
		self.log("Enqueueing message to %s" % queue, level = logging.INFO)
		self.output_queue_system.add(queue, json.dumps(message))

	def _start_running(self):
		""" Mark the current PDU as running. """
		self._running = True

	def _stop_running(self):
		""" Mark the current PDU as NOT running. """
		self._running = False

	def _is_running(self):
		""" Query whether the current PDU is running or not. """
		result = self._running
		return result


	def acquire_data(self):
		#It should be designed to return a list of messages, as it is possible to retrieve multiple datasets at once
		raise NotImplemented("Please implement this in your sub-class!")

	def run(self):
		self._start_running()
		self.log("DAU %s is alive!" %self.__class__.__name__)

		while self._is_running():
			messages = self.acquire_data()
			for msg in messages:
				self.send_to(self.QUEUE, msg)
			time.sleep(self.DATA_SAMPLING_FREQUENCY /1000.0)