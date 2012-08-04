import threading
import kestrel
import time
import config
import zlib
import pickle

class SensorSampler(threading.Thread):
    '''
        Base class implemented by all objects which retrieve data from a sensor.
        Interesting parameters for such a class:
        - frequency (0 for continuous polling or a value in ms representing
                     the minimal pause between two measurements). Default
                     is 100 ms.
        - name of queue on which to write
        - reported type of sensor
        - other meta data (via the other_metadata() function)
    '''
    QUEUE_NAME = 'sensor_values'
    SENSOR_TYPE = None
    FREQUENCY = 100 # ms
    
    def __init__(self):
        self.running = False
        self.kestrel_client = kestrel.Client(config.get_kestrel_servers())
        threading.Thread.__init__(self)
    
    def __del__(self):
        self.kestrel_client.close()
    
    def get_sensor_value(self):
        '''
            Override this in your class and make it return the value of the
            sensor. For example, in a webcam, the "value" is the RGB
            image.
        '''
        raise NotImplementedError('Implement this in your class!')
    
    def other_metadata(self):
        '''
            Override this in your class to return custom meta-data that
            will be transmitted together with the sensor values.
        '''
        return {}
    
    def start_sampling(self):
        '''
            Start sensor sampling. This also calls Thread.start() 
        '''
        self.running = True
        self.start() 
    
    def stop_sampling(self):
        '''
            Stop sensor sampling. This also calls Thread.join()
        '''
        self.running = False
        self.join(10) # Max 10s wait time
    
    def run(self):
        '''
            Start a sensor sampling loop.
        '''
        while self.running:
            # Get the sensor value and write it to the queue
            now = time.time()
            value = self.get_sensor_value()
            compressed_value = zlib.compress(pickle.dumps(value))
            doc = {
                'compressed_value': compressed_value,
                'measured_at': int(now),
                'sensor_type': self.SENSOR_TYPE
            }
            self.kestrel_client.add(self.QUEUE_NAME, pickle.dumps(doc))
            now2 = time.time()
            
            # Compute the remaining time to sleep
            time_diff_ms = int((now2 - now) * 1000)
            remaining_ms = max(time_diff_ms - self.FREQUENCY, 0)
            
            # Sleep if needed in order to avoid overflowing of the queues.
            if remaining_ms > 0:
                time.sleep(remaining_ms * 1.0 / 1000)

class SensorConsumer(threading.Thread):
    '''
        Base class for consuming sensor values.
    '''
    QUEUE_NAME = 'sensor_values'
    
    def __init__(self):
        self.running = False
        self.kestrel_client = kestrel.Client(config.get_kestrel_servers())
        threading.Thread.__init__(self)
    
    def __del__(self):
        self.kestrel_client.close()
        
    def start_consuming(self):
        '''
            Start consuming sensor values. This also calls Thread.start()
        '''
        self.running = True
        self.start()
        
    def stop_consuming(self):
        '''
            Stop consuming sensor values. This also calls Thread.join()
        '''
        self.running = False
        self.join(10)
        
    def consume(self, value):
        '''
            Override this in your class in order to implement consuming of
            sensor values.
        '''
        raise NotImplementedError('Implement this in your class!')
        
    def run(self):
        '''
            Main loop of the consumer, which retrieves items from the queue
            and consumes them by calling self.consume().
            
            NOTE: items are passed in deserialized form to self.consume()
        '''
        while self.running:
            # Retrieve an item from the queue and deserialize it
            measurement = self.kestrel_client.get(self.QUEUE_NAME, 10)
            
            # Queue must be empty, so retry
            if measurement is None:
                continue
                
            measurement = pickle.loads(measurement)
            
            # If the measurement contains a compressed value
            # (useful for stuff like frames), then decompress it.
            if 'compressed_value' in measurement:
                value = measurement['compressed_value']
                measurement['value'] = pickle.loads(zlib.decompress(value))
            
            self.consume(measurement)
            