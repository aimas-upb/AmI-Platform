import math

import cv

from core import PDU

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

    def process_message(self, message):
        if message['sensor_type'] == 'kinect' and message['type'] =='skeleton':
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
            
            # some temp variables manipulation follows as the cv library uses
            # output parameters on multilications'''
            
            temp_mat = cv.CreateMat(3,3, cv.CV_64F)
            rot_mat = cv.CreateMat(3,3, cv.CV_64F)
            
            cv.MatMul(ry,rx,temp_mat)
            cv.MatMul(temp_mat, rz, rot_mat)
            
            pos = cv.CreateMat(3,1, cv.CV_64F)
            temp_pos = cv.CreateMat(3,1, cv.CV_64F)
            
            torso_pos = message['skeleton_3D']['torso']
            pos[0,0] = torso_pos['X']
            pos[1,0] = torso_pos['Y']
            pos[2,0] = torso_pos['Z']
            
            cv.MatMul(rot_mat, pos, temp_pos)
            
            pos[0,0] = temp_pos[0,0] + sensor_position['X']
            pos[1,0] = temp_pos[1,0] + sensor_position['Y']
            pos[2,0] = temp_pos[2,0] + sensor_position['Z']
            
            position_message = {}
            position_message['X'] = pos[0,0]
            position_message['Y'] = pos[1,0]
            position_message['Z'] = pos[2,0]
            
            position_message['sensor_id'] = message['sensor_id']
            position_message['created_at'] = message['created_at']
            
            if 'player' in message:
                position_message['player'] = message['player']
            
            self.log('Found position %s' % position_message)
            self.send_to('subject-position', {'subject_position': position_message})
            
        return None

def rot_x(phi):
    mat = cv.CreateMat(3,3, cv.CV_64F)
    cv.Set(mat, 0.0)
    mat[0,0] = 1
    mat[1,1] = math.cos(phi)
    mat[1,2] = - math.sin(phi)
    mat[2,1] = math.sin(phi)
    mat[2,2] = math.cos(phi)
    return mat

def rot_y(phi):
    mat = cv.CreateMat(3,3, cv.CV_64F)
    cv.Set(mat, 0.0)    
    mat[0,0] = math.cos(phi)
    mat[0,2] = math.sin(phi)
    mat[1,1] = 1
    mat[2,0] = - math.sin(phi)
    mat[2,2] = math.cos(phi)
    return mat

def rot_z(phi):
    mat = cv.CreateMat(3,3, cv.CV_64F)
    cv.Set(mat, 0.0)    
    mat[0,0] = math.cos(phi)
    mat[0,1] = - math.sin(phi)    
    mat[1,0] = math.sin(phi)
    mat[1,1] = math.cos(phi)    
    mat[2,2] = 1
    
    return mat

if __name__ == "__main__":
    module = RoomPosition()
    module.run()