import json
import logging
import SocketServer
import socket
import time

from core import DAU
from lib.log import setup_logging
from lib.dashboard_cache import DashboardCache

class Arduino(DAU):

    QUEUE = 'measurements'
    DATA_SAMPLING_FREQUENCY = None #set to None as this DAU does not work by polling
    REQUIRED_KEYS = ['temperature', 'sensor_id', 'created_at', 'sensor_type', 'distance', 'luminosity']
    ENVIRONMENT_LIMIT = 1000
    
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
            
    def valid(self, j):
        if not all([(k in j) for k in self.REQUIRED_KEYS]):
            return False
        min_time = 1000 * (time.time() - 365.0 * 24  * 3600)
        max_time = 1000 * (time.time() + 10.0 * 24 * 3600)
        if j['created_at'] > max_time or j['created_at'] < min_time:
            return False
        return True
    
    def handle(self, request):
        try:
            request.settimeout(2)
            string = request.recv(1024)
            data = json.loads(string)
            if self.valid(data):
                self.handle_arduino_data(data)
            else:
                self.log('Invalid data %s' % string, logging.WARN)
        except ValueError:
            self.log('Error parsing from client %s' % string, logging.WARN)
        except socket.timeout:
            self.log('Timeout reading from client', logging.WARN)

    def handle_arduino_data(self, data):
        self.transform_data(data)
        data['type'] = 'environment'
        #TODO get this values in a list by sensor_id
        data['sensor_position'] = {'X': 0, 'Y': 0, 'Z': 0, 'alpha': 0, 'beta': 0, 'gamma': 0}
        self.send_to(self.QUEUE, data)
        
        len = self.dashboard_cache.lpush(sensor_id=data['sensor_id'],
            sensor_type=data['sensor_type'],
            measurement_type=data['type'],
            measurement=json.dumps(data))
        if len > 2 * self.ENVIRONMENT_LIMIT:
            self.dashboard_cache.ltrim(sensor_id=data['sensor_id'],
               sensor_type=data['sensor_type'],
               measurement_type=data['type'],
               start=0,
               stop=self.ENVIRONMENT_LIMIT)
        pass
    
    def transform_data(self, data):
        data['temperature'] = self.transform_temp(data.get('temperature', 0))
        data['humidity'] = self.transform_humid(data.get('humidity', 0))
        data['distance'] = self.transform_distance(data.get('distance', 0))

    def transform_distance(self, x):
        #f(x)=-4.1851e-11*x^5+7.2415e-08*x^4-4.9933e-05*x^3+1.7507e-02*x^2-3.2949e+00*x+3.1727e+02                                                        
        return -4.1851e-11 * pow(x, 5) + 7.2415e-08 * pow(x, 4) - 4.9933e-05 * pow(x, 3) + \
            1.7507e-02 * pow(x,2) - 3.2949 * x + 3.1727e+02
    
    def transform_temp(self, temp):
        return temp * 0.01 - 40
    
    def transform_humid(self, h):
        return h * h * -2.8e-06 + h * 0.0405 - 4

        
    def startup(self):
        if self.server is not None:
            self.shutdown()
    
        def make_handler(request, client_address, server):
            return Arduino.TCPRequestHandler(self, request, client_address, server)
        
        HOST, PORT = "0.0.0.0", 5500
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
        self.log("DAU %s is alive!" %self.__class__.__name__)
        
    
if __name__ == '__main__':
    setup_logging()
    module = Arduino()
    module.run()
