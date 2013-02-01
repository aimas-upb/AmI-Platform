import logging
import time
import threading
from unittest import TestCase

from core.kestrel_mock import KestrelMock
from core.measurements_player import MeasurementsPlayer

logger = logging.getLogger(__name__)

class PipelineTest(TestCase):

	PDUs = []
	DATA_FILE = None
	DELAY_UNTIL_MESSAGES_PROPAGATE = 30

	def setUp(self):
		""" Set-up of the pipeline test:
			- set up the mocked queue system
			- set up the measurements player
			- set up the PDUs as threads
		"""
		super(PipelineTest, self).setUp()
		self._setup_queue_system()
		self._setup_player()
		self._setup_pdus()
		logging.basicConfig()

	def _test_pipeline(self):
		""" Each such test class will contain only one test method,
		that will start the pipeline and perform a basic test. """

		# Start PDUs
		for thread in self._thread_pool:
			thread.start()

		# Start the player, and wait for it to finish pumping the measurements
		# into the pipeline.
		self._player_thread.start()
		self._player_thread.join()

		# Wait for another 30 seconds to give the measurements time to propagate
		# through the pipeline. Then we will abruptly close down all the
		# PDUs (with a thread.join with small timeout)
		time.sleep(self.DELAY_UNTIL_MESSAGES_PROPAGATE)

		# Close down the PDUs forcibly
		self._close_down_pdus()

		# Perform the custom check
		self.check_results()

	def check_results(self):
		""" Method that gets called after the experiment is ran in order
		to check that everything went OK.

		Suggested uses:
			- check the queues for stuff
			- check that API calls to external services were made

		"""
		raise Exception("Please implement this in your test")

	def _enqueue_on_measurements(self, measurement):
		""" Callback for the measurements player that actually takes
		each measurement and puts it on the 'measurements' queue
		of the mocked queue system. """
		self._queue_system.add('measurements', measurement)

	def _setup_queue_system(self):
		""" Set-up the mocked queue system used by this test. """
		logger.info("Setting up mocked queue system")
		self._queue_system = KestrelMock()

	def _measurements_player_instance(self, **kwargs):
		""" Obtain a measurements player instance. """
		return MeasurementsPlayer(**kwargs)

	def _setup_player(self):
		""" Set-up the measurements player used by this test. """
		player_params = {
			'data_file': self.DATA_FILE,
			'callback': self._enqueue_on_measurements
		}
		self._player = self._measurements_player_instance(**player_params)

		# Player also needs to be ran on another thread.
		self._player_thread = threading.Thread(target = self._player.play)
		logger.info("Started measurements player thread")

	def _setup_pdus(self):
		""" Each PDU must be instantiated on a separate thread, because
		each PDU has an event loop based on polling.

		The PDUs will be connected among them via the mocked queue system,
		which removes the need to have Kestrel installed on your machine
		in order to run a pipeline test.
		"""
		self._thread_pool = []
		self._pdu_instances = []
		for pdu in self.PDUs:
			logger.info("Starting PDU with class %r" % pdu)
			pdu_instance = pdu(queue_system = self._queue_system)
			# Run each PDU on a thread
			pdu_thread = threading.Thread(target = pdu_instance.run)
			self._thread_pool.append(pdu_thread)
			self._pdu_instances.append(pdu_instance)

	def _close_down_pdus(self):
		""" Close down each PDU by signalling to it that it's not
			running anymore and waiting with a timeout of 1 for the
			corresponding thread to join. """

		# Signal to the PDUs that we're shutting down
		logger.info("Signalling to PDUs that it's time to go to sleep")
		for pdu_instance in self._pdu_instances:
			pdu_instance.stop()

		# Stop the PDU threads
		logger.info("Joining PDU threads")
		for pdu_thread in self._thread_pool:
			pdu_thread.join(0.1)

		logger.info("Finished joining PDU threads")
