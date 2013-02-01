from unittest import TestCase
import time
import threading

from core.pdu import PDU
from pipeline.measurements_player import MeasurementsPlayer


class PipelineTest(TestCase):

	PDUs = []
	DATA = ''
	QS = None

	def __init__(self):
		self.player = self.measurements_player(data_file = self.DATA, 
											   callback = lambda m: QS.add('measurements', m))
		thread_pool = []
		for pdu in PDUs:
			p = pdu(queue_system = QS)
			# run each PDU on a thread
			pduThread = threading.Thread(target = p.run)
			thread_pool.append(pduThread)
			pduThread.start()

		# run player on a separate thread
		playerThread = threading.Thread(target=self.player.play)
		playerThread.start()
		playerThread.join()

		# wait 30 seconds, then signal to PDUs that they have to go to sleep
		time.sleep(30)
		for thread in thread_pool:
			thread.join(timeout = 30)

		# call result_ok() function an see if it's ok
		results_ok()

	def measurements_player(self, data_file, callback):
		return MeasurementsPlayer(data_file = data_file, callback = callback)


class TestPipelineTest(PipelineTest):

	def measurements_player(self, data_file, callback):
		return DummyMeasurementsPlayer(data_file = data_file,
									   callback = callback, 
									   hardcoded_msgs = [{'a': 'b'}, {'c': 'd'}])

	def results_ok(self):
		m1 = QS.get('dummy')
		eq_(m1, {'a': 'b'}, 'm1 should have correct value')

		m2 = QS.get('dummy')
		eq_(m2, {'c': 'd'}, 'm2 should have correct value')


class DummyMeasurementsPlayer(MeasurementsPlayer):

	def __init__(self, data_file = None, callback = None, hardcoded_msgs = []):
		pass

	def play(self):
		for msg in hardcoded_msgs:
			self.callback(msg)

class DummyPDU(PDU):
	QUEUE = 'measurements'

	def process_message(self, message):
		self.send_to('dummy', message)


