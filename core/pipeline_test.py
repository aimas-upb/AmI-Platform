from unittest import TestCase
import time
import threading

from core.pdu import PDU
from pipeline.measurements_player import MeasurementsPlayer

class PipelineTest(TestCase):

	PDUs = []
	DATA = None
	QS = KestrelMock()

	def setUp(self):
		self.player = self.measurements_player(data_file = self.DATA, 
											   callback = lambda m: self.QS.add('measurements', m))
		thread_pool = []
		for pdu in self.PDUs:
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

