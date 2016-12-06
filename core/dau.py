import json
import logging
import pymongo
import settings
import threading
import time

from kestrel_connection import KestrelConnection

"""
	Data Acquisition Unit for Ami-Lab framework
	Its architecture resembles the design of PDU Class.
"""
class DAU(object):
	
	def __init__(self, **kwargs):
		""" Set-up connections to Mongo and Kestrel by default on each PDU. """
		self.queue_system = kwargs.get('queue_system', None) or KestrelConnection()
		self._mongo_connection = pymongo.Connection(settings.MONGO_SERVER)
		self._last_stats = time.time()
		self._processed_messages = 0
		self._running = False
		self._running_lock = threading.Lock()
		self.debug_mode = kwargs.get('debug', False)
		self.logger = logging.getLogger(self.__module__)
		
	def log(self, message, level = logging.INFO):
		self.logger.log(level, message)
		
	@property	
	def mongo_connection(self):
		return self._mongo_connection
		
	def send_to(self, queue, message):
		""" Send a message to another queue. """
		self.log("Enqueueing message to %s" % queue, level = logging.INFO)
		self.queue_system.add(queue, json.dumps(message))

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