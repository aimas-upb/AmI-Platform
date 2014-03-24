import numpy.linalg
import math

joints = ['head', 'neck', 'left_shoulder', 'left_hand', 
          'left_knee', 'right_elbow', 'right_shoulder', 
          'right_hand', 'left_hip', 'right_hip', 'left_foot', 
          'left_elbow', 'torso', 'right_knee', 'right_foot']

triples = [ 
    ('head'            , 'neck'           , 'left_shoulder'),   
    ('head'            , 'neck'           , 'right_shoulder'),  
    ('neck'            , 'left_shoulder'  , 'left_elbow'),      
    ('neck'            , 'right_shoulder' , 'right_elbow'),     
    ('left_shoulder'   , 'left_elbow'     , 'left_hand'),       
    ('right_shoulder'  , 'right_elbow'    , 'right_hand'),      
    ('head'            , 'neck'           , 'torso'),           
    ('neck'            , 'torso'          , 'left_hip'),
    ('neck'            , 'torso'          , 'right_hip'),       
    ('torso'           , 'left_hip'       , 'left_knee'),       
    ('torso'           , 'right_hip'      , 'right_knee'),      
    ('left_hip'        , 'left_knee'      , 'left_foot'),       
    ('right_hip'       , 'right_knee'     , 'right_foot'),      
    ('neck'            , 'torso'          , 'left_knee'),       
    ('neck'		       , 'torso'          , 'right_knee')      
]

pairs = [
    ('neck',            'torso'),
    ('left_shoulder',   'left_elbow'),
    ('right_shoulder',  'right_elbow')
]

def all_features(skeleton_3d):
    """Returns a list with all the features of interest for a give skeleton (as json)"""
    features = []
    features.extend(all_segment_to_segment(skeleton_3d))
    features.extend(all_segment_to_plane(skeleton_3d))
    return features

def all_segment_to_plane(skeleton_3d):
    """Returns all the features of type angle of segment to plane
        - skeleton_3d is a json skeleton_3d object
    """
    points = {}
    for j in joints:
        points[j] = point_of_json(skeleton_3d[j])
    inRad = []
    for plane in [1, 2]:
        inRad.extend([segment_to_plane(pair, points, plane) for pair in pairs])
    return [radToDeg(rad) for rad in inRad]

def all_segment_to_segment(skeleton_3d):
    """Returns all the features of type angle of segment to segment
        - skeleton_3d is a json skeleton_3d object
    """
    points = {}
    for j in joints:
        points[j] = point_of_json(skeleton_3d[j])
    
    inRad =  [segment_to_segment(triple, points) for triple in triples]
    return [radToDeg(rad) for rad in inRad]

def segment_to_plane(pair, points, plane):
    """Computes the angle between the segment given by the two joints in pair and the
    plane (1- xOy, 2- yOz). The points dictionary gives the coordinates of the joints"""
    if (plane == 1):
        return vector_to_xOy(points[pair[0]], points[pair[1]])
    elif (plane ==2):
        return vector_to_yOz(points[pair[0]], points[pair[1]])
    else:
        raise "Unknown plane: %d" % plane

def segment_to_segment(triple, points):
    """ compute the angles between the segments specified by the joint names in
    triple and given their actual location in the points dictionary"""
    p1 = points[triple[0]]
    p2 = points[triple[1]]
    p3 = points[triple[2]]
    
    return vector_angle_3d(vector_of_points(p2, p1), vector_of_points(p3, p2)) 

def radToDeg(rad):
    return rad / math.pi * 180

def vector_of_points(p2, p1):
    """ Returns  the vector given by the two 3D points"""
    return [p2[0] - p1[0], p2[1]- p1[1], p2[2] - p1[2]]

def vector_angle_3d(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'    """
    cosang = numpy.dot(v1, v2)
    sinang = numpy.linalg.norm(numpy.cross(v1, v2))
    return numpy.arctan2(sinang, cosang)

def vector_to_xOy(p1, p2):
    """ computes the angle between the vector given by two points and the xOy plane """
    v1 = vector_of_points(p1, p2)
    v2 = [0, 0, 1]#normal vector to the xOy plane
    
    return math.pi / 2 - vector_angle_3d(v1, v2)
    
def vector_to_yOz(p1, p2):
    """ computes the angle between the vector given by two points and the yOz plane """
    v1 = vector_of_points(p1, p2)
    v2 = [1, 0, 0]#normal vector to the yOz plane
    
    return math.pi / 2 - vector_angle_3d(v1, v2)

def point_of_json(obj):
    """extracts a float vector from a json object with X,Y,Z keys"""
    return [obj['X'], obj['Y'], obj['Z']]
    