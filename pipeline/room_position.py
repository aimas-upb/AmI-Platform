import json
import math

import cv

from core import PDU
from lib.dashboard_cache import DashboardCache
from lib.log import setup_logging
from lib.session_tracker import SessionTracker

class RoomPosition(PDU):
    ''' PDU that reads skeleton messages from kinect and translates the position 
        of the torso (from kinect coordinates) to room coordinates using the
        sensor position value that is sent by kinect.
        
        INPUT: 
        Message from kinect of skeleton type with sensor_position field
        The sensor_position needs the following fields:
            - X,Y,Z: the position of the sensor wrt the room
            - alpha: the rotation around y axis
            - beta: the rotation around x axis
            - gamma: the rotation around z axis
        The message needs a skeleton_3D key with the positions of the torso
        
        OUTPUT:
        Sends a message with a subject_position key set to a dictionary with 
        X,Y,Z in room coordinates. The message is sent to the subject-position
        queue
    '''
    
    QUEUE = 'room-position'
    #torso is always first in list
    JOINTS = ['torso', 'head', 'neck', 'left_shoulder', 'right_shoulder', 
              'left_elbow', 'right_elbow', 'left_hand', 'right_hand', 
              'left_hip', 'right_hip', 'left_knee', 'right_knee', 
              'left_foot', 'right_foot']

    def __init__(self, **kwargs):
        super(RoomPosition, self).__init__(**kwargs)
        self.session_tracker = SessionTracker()
        self.dashboard_cache = DashboardCache()

    def process_message(self, message):
        if message['type'] !=  'skeleton':
            return
        
        sensor_position = message['sensor_position']
        """ We are doing rotation using the euler angles
            see http://en.wikipedia.org/wiki/Rotation_matrix
        """
        alpha = sensor_position['alpha']
        beta = sensor_position['beta']
        gamma  = sensor_position['gamma']
        
        rx = rot_x(beta)
        ry = rot_y(alpha)
        rz = rot_z(gamma)
        trans = tanslation(sensor_position['X'], sensor_position['Y'], sensor_position['Z'])
        
        # some temp variables manipulation follows as the cv library uses
        # output parameters on multilications
        
        temp_mat = cv.CreateMat(4,4, cv.CV_64F)
        rot_mat = cv.CreateMat(4,4, cv.CV_64F)         
        
        cv.MatMul(ry,rx,temp_mat)
        cv.MatMul(temp_mat, rz, rot_mat)
        cv.MatMul(trans, rot_mat, temp_mat)
        
        N = len(self.JOINTS)
        pos = cv.CreateMat(4, N, cv.CV_64F)
        temp_pos = cv.CreateMat(4, N, cv.CV_64F)
        skeleton_3D = message['skeleton_3D']
        
        for i in range(N):
            joint = self.JOINTS[i]
            if joint in skeleton_3D:
                joint_pos = skeleton_3D[joint]
                temp_pos[0,i] = joint_pos['X']
                temp_pos[1,i] = joint_pos['Y']
                temp_pos[2,i] = joint_pos['Z']
                temp_pos[3,i] = 1
    
        cv.MatMul(temp_mat, temp_pos, pos)
        skeleton_in_room = {}
        for i in range(N):
            joint = self.JOINTS[i]
            if joint in skeleton_3D:
                skeleton_in_room[joint] = {
                    'X': pos[0, i],
                    'Y': pos[1, i],
                    'Z': pos[2, i],
                }
        
        position_message = {
            'X': pos[0,0],
            'Y': pos[1,0],
            'Z': pos[2,0],
        }
        
        self.log('Found position %s' % position_message)
        
        if message.get('session_id', None):
            sid = message['session_id']
            time = message['created_at']
            self.session_tracker.track_event(sid, time, {'skeleton_in_room': skeleton_in_room})
            self.session_tracker.track_event(sid, time, {'subject_position': position_message})
        
        dashboard_message = {'created_at': message['created_at'], 'sensor_id': message['sensor_id']}
        dashboard_message.update(position_message)
        
        # Send subject position to Redis
        self.dashboard_cache.lpush(sensor_id=message['sensor_id'],
            sensor_type=message['sensor_type'],
            measurement_type='subject_position',
            measurement=json.dumps(dashboard_message))
                
        return None

def tanslation(x,y,z):
    mat = cv.CreateMat(4,4, cv.CV_64F)
    cv.Set(mat, 0.0)    
    mat[0,0] = 1
    mat[0,3] = x
    mat[1,1] = 1
    mat[1,3] = y
    mat[2,2] = 1
    mat[2,3] = z
    mat[3,3] = 1
    return mat
    

def rot_x(phi):
    mat = cv.CreateMat(4,4, cv.CV_64F)
    cv.Set(mat, 0.0)
    mat[0,0] = 1
    mat[1,1] = math.cos(phi)
    mat[1,2] = - math.sin(phi)
    mat[2,1] = math.sin(phi)
    mat[2,2] = math.cos(phi)
    mat[3,3] = 1
    return mat

def rot_y(phi):
    mat = cv.CreateMat(4,4, cv.CV_64F)
    cv.Set(mat, 0.0)    
    mat[0,0] = math.cos(phi)
    mat[0,2] = math.sin(phi)
    mat[1,1] = 1
    mat[2,0] = - math.sin(phi)
    mat[2,2] = math.cos(phi)
    mat[3,3] = 1
    return mat

def rot_z(phi):
    mat = cv.CreateMat(4,4, cv.CV_64F)
    cv.Set(mat, 0.0)    
    mat[0,0] = math.cos(phi)
    mat[0,1] = - math.sin(phi)    
    mat[1,0] = math.sin(phi)
    mat[1,1] = math.cos(phi)    
    mat[2,2] = 1
    mat[3,3] = 1
    
    return mat

if __name__ == "__main__":
    setup_logging()
    module = RoomPosition()
    module.run()
