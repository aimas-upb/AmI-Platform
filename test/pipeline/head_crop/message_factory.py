from random import Random

_r = Random()

def image_message(sensor_id = '1', created_at = 0, size = (640, 480)):
    return {
        'sensor_type': 'kinect',
        'sensor_id': sensor_id,
        'created_at': created_at,
        'type': 'image_rgb',
        'image_rgb': {
            'image': 'A' * (size[0] * size[1] * 3 * 4/3),
            'width': size[0],
            'height': size[1]
        }
    }

def skeleton_message(sensor_id = '1', created_at = 0, head = None, neck = None):
    
    if head is None:
        head = {'X': _r.random() * 640, 'Y': _r.random() * 480}
        
    if neck is None:
        neck = {'X': _r.random() * 640, 'Y': _r.random() * 480}
        
    return {
        'sensor_type': 'kinect',
        'sensor_id': sensor_id,
        'created_at': created_at,
        'type': 'skeleton',
        'skeleton_2D': {'head': {'X': 1.0, 'Y': 2.0}, 'neck': {'X': 3.0, 'Y':4.0}}
    }