import json
import logging
import SocketServer
import socket
import time
import sys
import itertools
import numbers
import types

sys.path.append('/home/ami/AmI-Platform/')
from core import DAU
from lib.log import setup_logging
from lib.dashboard_cache import DashboardCache


class Arduino_DAU(DAU):

    QUEUE = 'measurements'
    REQUIRED_KEYS = ['s_type', 's_id','t','h', 'd', 'l']

    ARDUINO_INCOMING_SERVER_IP = '192.168.0.101'
    ARDUINO_INCOMING_SERVER_PORT = 5500

    ARDUINO_IDS = ['-'.join(x) for x in itertools.product(['K' + str(x) for x in range(1, 20)],['A','B','C'])]

    def __init__(self, **kwargs):
        super(Arduino_DAU, self).__init__(**kwargs)
        self.server = None
        self.dashboard_cache = DashboardCache()

    class TCPRequestHandler(SocketServer.BaseRequestHandler):
        def __init__(self, arduino, request, client_address, server):
            self.arduino = arduino
            SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)

        def handle(self):
            self.arduino.handle(self.request)

    def validate_message(self, message):
        if message['s_type'] != 'arduino':
            self.log('sensor type %s' % message['s_type'])
            return False

        if message['s_id'] not in self.ARDUINO_IDS:
            self.log('sensor id %s' % message['s_id'])
            return False

        if not isinstance(message['t'], numbers.Real):
            self.log('sensor temperature %s' % message['t'])
            return False

        if not isinstance(message['h'], numbers.Real):
            self.log('humidity %s' % message['h'])
            return False

        if not isinstance(message['l'], numbers.Real):
            self.log('luminosity %s' % message['l'])
            return False

        return True

    def handle(self, request):
        try:
            request.settimeout(2)
            string = request.recv(1024)
            arduino_data = json.loads(string)
            print("Am primit: " + string)
            if self.validate_message(arduino_data):
                self.handle_arduino_data(arduino_data)
            else:
                self.log('Invalid data %s' % string, logging.WARN)
                print("Invalid data")
        except ValueError:
            self.log('Error parsing from client %s' % string, logging.WARN)
            print("Error parsing")
        except socket.timeout:
            self.log('Timeout reading from client', logging.WARN)
            print("Timeout reading")

    def handle_arduino_data(self, arduino_data):
        data = {}

        data['sensor_id'] = arduino_data['s_id']
        data['temperature'] = arduino_data['t']
        data['humidity'] = arduino_data['h']
        data['luminosity'] = arduino_data['l']
        data['created_at'] = int(time.time())
        data['sensor_type'] = 'arduino'
        if 'd' in arduino_data:
            data['distance'] = arduino_data['d']
            data['type'] = 'distance'
        else:
            data['type'] = 'environment'

        self.send_to(self.QUEUE, data)
        return

    def startup(self):
        if self.server is not None:
            self.shutdown()

        def make_handler(request, client_address, server):
            return Arduino_DAU.TCPRequestHandler(self, request, client_address, server)

        HOST, PORT = self.ARDUINO_INCOMING_SERVER_IP, self.ARDUINO_INCOMING_SERVER_PORT
        server = SocketServer.TCPServer((HOST, PORT), make_handler)

        self.log('Server listening')

        # test = {}
        # test['sensor_id'] = 'ARDUINO_DAU_SERVER'
        # test['sensor_type'] = 'arduino'
        # test['type'] = 'start_up_test'
        # self.send_to(self.QUEUE, test)

        server.serve_forever()
        # Exit the server thread when the main thread terminates

    def shutdown(self):
        if self.server is not None:
            self.log('Server shutting down')
            self.server.shutdown()
            self.server = None

    def _start_running(self):
        super(Arduino_DAU, self)._start_running()
        self.startup()

    def _stop_running(self):
        self.shutdown()
        super(Arduino_DAU, self)._stop_running(self)

    def run(self):
        self._start_running()
        self.log("DAU %s is alive!" % self.__class__.__name__)


if __name__ == '__main__':
    setup_logging()
    module = Arduino_DAU()
    module.run()
