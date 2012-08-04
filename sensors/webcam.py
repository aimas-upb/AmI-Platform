import sensors
import cv2

class WebcamSensorSampler(sensors.SensorSampler):
    '''
        Sensor sampler based on OpenCV.
    '''
    SENSOR_TYPE = 'webcam'
    
    def __init__(self):
        self.video_capture = cv2.VideoCapture(0)
        sensors.SensorSampler.__init__(self)
        
    def __del__(self):
        self.video_capture.release()
        sensors.SensorSampler.__del__(self)
    
    def get_sensor_value(self):
        '''
            Retrieve a frame from the webcam.
        '''
        _, frame = self.video_capture.read()
        return frame

class WebcamDisplaySensorConsumer(sensors.SensorConsumer):
    '''
        Sensor consumer that displays images using OpenCV
    '''
    
    def __init__(self):
        cv2.namedWindow("webcam")
        sensors.SensorConsumer.__init__(self)
    
    def __del__(self):
        cv2.destroyWindow("webcam")
        sensors.SensorConsumer.__del__(self)
        
    def consume(self, value):
        '''
            Consume a value by displaying it if its type is webcam.
        '''
        img = value['value']
        print "len = %d" % (len(img))
        cv2.imshow("webcam", img)
        if cv2.waitKey(5)==27:
            self.running = False
        