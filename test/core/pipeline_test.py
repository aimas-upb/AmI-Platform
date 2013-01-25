from core import PipelineTest, PDU

class TestPipelineTest(PipelineTest):
	def measurements_player(self, data_file, callback):
		return DummyMeasurementsPlayer(data_file = data_file,
									   callback = callback, 
									   hardcoded_msgs = [{'a': 'b'}, {'c': 'd'}])

	def test_results_ok(self):
		m1 = self.QS.get('dummy')
		eq_(m1, {'a': 'b'}, 'm1 should have correct value')

		m2 = self.QS.get('dummy')
		eq_(m2, {'c': 'd'}, 'm2 should have correct value')
		

class DummyMeasurementsPlayer(object):

	def __init__(self, data_file = None, callback = None, hardcoded_msgs = []):
		self.callback = callback
		self.hardcoded_msgs= hardcoded_msgs

	def play(self):
		for msg in self.hardcoded_msgs:
			self.callback(msg)

class DummyPDU(PDU):
	QUEUE = 'measurements'

	def process_message(self, message):
		self.send_to('dummy', message)