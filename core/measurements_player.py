import time
import json

from experiment_file import ExperimentFile

class MeasurementsPlayer(object):

	def __init__(self, data_file, callback):
		self.data_file = data_file
		self.callback = callback
		self.experiment_file = ExperimentFile(self.data_file)

	def play(self):
		playback_start = int(time.time())
		measurement_start = None

		for measurement in self.experiment_file.open_for_reading():
			if not measurement_start:
				measurement_start = measurement['created_at']

			playback_delta = int(time.time()) - playback_start
			measurement_delta = measurement['created_at'] - measurement_start

			if playback_delta < measurement_delta:
				# Sleep in order to wait for the correct time to play
				# back this measurement.
				time.sleep(measurement_delta - playback_delta)
			else:
				# Skip this measurement because we're behind
				continue

			self.callback(json.dumps(measurement))

		self.experiment_file.close()