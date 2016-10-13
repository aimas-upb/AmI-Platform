import json
import logging
import SocketServer
import socket
import time

from core import DAU
from lib.log import setup_logging
from lib.dashboard_cache import DashboardCache


class Arduino_DAU(DAU):

    QUEUE = 'measurements'
    REQUIRED_KEYS = ['s_type', 's_id','t','h', 'd', 'l']

    ARDUINO_INCOMING_SERVER_IP = '192.168.0.101'
    ARDUINO_INCOMING_SERVER_PORT = '5500'


    def __init__(self, **kwargs):
        super(Arduino, self).__init__(**kwargs)
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

        if message['s_id'] not in ['K' + str(x) for x in range(1, 20)]:
            self.log('sensor id %s' % message['s_id'])
            return False

        if not isinstance(message['t'], numbers.Integral):
            self.log('sensor temperature %s' % message['t'])
            return False

        if not isinstance(message['h'], numbers.Integral):
            self.log('humidity %s' % message['h'])
            return False

        if not isinstance(message['d'], numbers.Integral):
            self.log('distance %s' % message['d'])
            return False

        if not isinstace(message['l'], numbers.Integral):
            self.log('luminosity %s' % message['l'])
            return False

        return True

    def handle(self, request):
        try:
            request.settimeout(2)
            string = request.recv(1024)
            arduino_data = json.loads(string)
            if self.validate_message(arduino_data):
                self.handle_arduino_data(arduino_data)
            else:
                self.log('Invalid data %s' % string, logging.WARN)
        except ValueError:
            self.log('Error parsing from client %s' % string, logging.WARN)
        except socket.timeout:
            self.log('Timeout reading from client', logging.WARN)

    def handle_arduino_data(self, arduino_data):
        data = json.dumps({})

        data['temperature']=arduino_data['l']
        data['humidity']=arduino_data['h']
        data['luminosity']=arduino_data['l']
        data['distance']=arduino_data['d']
        data['type'] = 'environment'
        data['created_at'] = data.get('created_at', int(time.time()))


        self.send_to(self.QUEUE, data)

    def startup(self):
        if self.server is not None:
            self.shutdown()

        def make_handler(request, client_address, server):
            return Arduino.TCPRequestHandler(self, request, client_address, server)

        HOST, PORT = ARDUINO_INCOMING_SERVER_IP, ARDUINO_INCOMING_SERVER_PORT
        server = SocketServer.TCPServer((HOST, PORT), make_handler)

        self.log('Server listening')
        server.serve_forever()
        # Exit the server thread when the main thread terminates

    def shutdown(self):
        if self.server is not None:
            self.log('Server shutting down')
            self.server.shutdown()
            self.server = None

    def _start_running(self):
        super(Arduino, self)._start_running()
        self.startup()

    def _stop_running(self):
        self.shutdown()
        super(Arduino, self)._stop_running(self)

    def run(self):
        self._start_running()
        self.log("DAU %s is alive!" % self.__class__.__name__)


if __name__ == '__main__':
    setup_logging()
    module = Arduino_DAU()
    module.run()
