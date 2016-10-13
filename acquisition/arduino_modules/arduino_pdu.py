import socket
import json
import numbers

from core import PDU, settings
from lib.log import setup_logging
from models.experiment import Experiment

class Arduino_PDU(PDU):
	#PDU communication with Arduino

	QUEUE = 'measurements'
	REQUIRED_KEYS = ['s_type', 's_id', 't', 'h', 'd', 'l']

	ARDUINO_LIGHT_CONTROLLER_IP = '192.168.0.102'
	ARDUINO_LIGHT_CONTROLLER_PORT = 2000


	def __init__(self, **kwargs):
		super(Arduino, self).__init__(**kwargs)


	def validate_message(self, message):

		if message['type'] == 'command_set':

			if message['target'] == 'lights'

				if message['light_front'] not in ['on', 'off']:
					self.log('server light_front %s' % message['light_front'])
					return False

				if message['light_back'] not in ['on', 'off']:
					self.log('server light_front %s' % message['light_back'])
					return False

			return True

		elif message['type'] == 'command_get':

			if message['target'] != 'lights'
				self.log('server target %s' % message['target'])
				return False

			return True

		else
			self.log('server message type %s' % message['type'])
			return false


	def process_message(self,message):

		'''
		1. receive command message
		2. execute the command (talk to the Arduino)
		3. compose ack message
		4. send ack message
		'''


		# TCP/IP Socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Define Server Address
		server_address = (ARDUINO_LIGHT_CONTROLLER_IP, ARDUINO_LIGHT_CONTROLLER_PORT);

		# Connect to Arduino Server
		sock.connect(server_address)
		self.log('Connecting to %s port %s' %server_address)

		#Data (json ) which will be send to Arduino
		data = json.dumps({})

		if message['type'] == 'command_set':

			data['target']=message['target']
			data['action']='set'
			data['timestamp']='1000'

			data['light_front'] = message['light_front']
			data['light_back'] = message['light_back']

		else

			data['target'] = message['target']
			data['action'] = 'set'
			data['timestamp'] = '1000'

		try:
			# Send data
			sock.sendall(data + '\n')
			self.log('sending to arduino: %s', % data)

			# Look for the response
			response = sock.recv(16)
			self.log('receiving from arduino: %s', % response)

			# TODO - validate response from Arduino before sending it back to the system

			# Send response to the new QUEUE
			self.send_to(self.QUEUE, response)

if __name__ == "__main__":
	setup_logging()
	module = Arduino_PDU()
	module.run()



