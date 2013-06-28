import math
from unittest import TestCase
import logging

from mock import patch
from nose.tools import eq_
from lib import log

from pipeline.room_position import RoomPosition, SessionTracker


@patch.object(SessionTracker, 'track_event')
class RoomPositionTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super(RoomPositionTest, cls).setUpClass()

        log.setup_logging(level=logging.DEBUG)

    def test_not_interesting_message(self, track_event):
        message = {'sensor_type': 'kinect',
                   'type': 'RGB'}
        rp = RoomPosition()
        rp.process_message(message)
        eq_(track_event.call_count, 0,
            "track_event should only be called if it has skeleton")

    def test_all(self, track_event):
        ''' The sensor is at origin '''
        self._run_test_with(track_event,
                           {'X': 0, 'Y': 0, 'Z': 0,
                            'alpha': 0.0, 'beta': 0.0, 'gamma': 0.0},
                           {'X': 10, 'Y': 20, 'Z': 30},
                           10, 20, 30)

        ''' The sensor axes are aligned with room axes. It is just translated'''
        self._run_test_with(track_event,
                           {'X': 20, 'Y': 30, 'Z': 40,
                            'alpha': 0.0, 'beta': 0.0, 'gamma': 0.0},
                           {'X': 10, 'Y': 20, 'Z': 30},
                           30, 50, 70)

        ''' The sensor is placed in the oposite corner of the room, and turned
            180 degrees around vertical'''
        self._run_test_with(track_event,
                           {'X': 4000, 'Y': 3000, 'Z': 1000,
                            'alpha': math.pi,
                            'beta': 0.0,
                            'gamma': 0.0},
                           {'X': 4000, 'Y': -3000, 'Z': 1000},
                           0, 0, 0)

        ''' The sensor is placed in the oposite corner of the room, and turned
            180 degrees around X'''
        self._run_test_with(track_event,
                           {'X': 4000, 'Y': 3000, 'Z': 1000,
                           'alpha': 0.0,
                           'beta': math.pi,
                           'gamma': 0.0},
                           {'X': -4000, 'Y': 3000, 'Z': 1000},
                           0, 0, 0)

        ''' The sensor is placed in the oposite corner of the room, and turned
            180 degrees around Z
        '''
        self._run_test_with(track_event,
                            {'X': 4000, 'Y': 3000, 'Z': 1000,
                            'alpha': 0.0,
                            'beta': 0.0,
                            'gamma': math.pi},
                            {'X': 4000, 'Y': 3000, 'Z': -1000},
                            0, 0, 0)

        ''' The sensor is placed on the oposite corner of the room, but
            on the floor and facing directly the origin of the room
        '''
        self._run_test_with(track_event,
                           {'X': 1000, 'Y': 0, 'Z': 1000,
                           'alpha': - 3 / 4. * math.pi,
                           'beta': 0,
                           'gamma': 0},
                           {'X': 0, 'Y': 0, 'Z': 1414.21356},
                           0, 0, 0)

        ''' The sensor is placed on the oposite corner of the room, facing
            directly the origin of the room
         '''
        beta = math.atan(1 / math.sqrt(2))
        self._run_test_with(track_event,
                           {'X': 1000, 'Y': 1000, 'Z': 1000,
                            'alpha': 5.0 / 4 * math.pi,
                            'beta':  beta,
                            'gamma': 0.0},
                           {'X': 0000, 'Y': 0000, 'Z': 1732.0508076},
                           0, 0, 0)

    def _run_test_with(self, track_event, sensor_pos, torso_pos,
                      expected_x, expected_y, expected_z):

        track_event.reset_mock()

        rp = RoomPosition()

        skeleton_3D = {}
        for j in rp.JOINTS:
            skeleton_3D[j] = torso_pos
        message = {'sensor_type': 'kinect',
                   'type': 'skeleton',
                   'sensor_position': sensor_pos,
                   'skeleton_3D': skeleton_3D,
                   'sensor_id': '10',
                   'created_at': 1,
                   'session_id': 'test:room-position'}

        expected = {'sensor_id': '10', 'created_at': 1}

        rp.process_message(message)
        eq_(track_event.call_count, 2)  # one for subject_position and one for skeleton_in_room
        track_event.assert_any_call('test:room-position', 1, PositionMatcher(
                                                                   expected_x,
                                                                   expected_y,
                                                                   expected_z,
                                                                   expected))


class AnyOf:

    def __init__(self, values):
        self.values = values

    def __eq__(self, other):
        return other in self.values


class PositionMatcher:

    def __init__(self, x, y, z, kwargs):
        self.x = x
        self.y = y
        self.z = z
        self.args = kwargs

    def __eq__(self, other):
        if other['type'] == 'subject_position':
            pos = other
            self.all_eq(pos) and self.check_kwargs(pos)
        elif other['type'] == 'skeleton_in_room':
            for pos in other['skeleton_3D'].itervalues():
                if not self.all_eq(pos):
                    return False
            return self.check_kwargs(other)

        return False

    def all_eq(self, pos):
        return _feq(self.x, pos['X']) \
            and _feq(self.y, pos['Y']) \
            and _feq(self.z, pos['Z'])

    def check_kwargs(self, pos):
        for k in self.args.keys():
            if self.args[k] != pos[k]:
                return False
        return True


def _feq(a, b, epsilon=0.00001):
    return abs(a - b) < epsilon
