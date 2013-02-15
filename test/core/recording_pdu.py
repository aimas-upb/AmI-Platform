from datetime import datetime
import time
from unittest.case import TestCase

from mock import patch
from mongoengine import connect
from nose.plugins.attrib import attr
from nose.tools import eq_

from core.recording_pdu import ExperimentFile, RecordingPDU
from models.experiment import Experiment

@patch.object(ExperimentFile, 'put', autospec=True)
@patch.object(ExperimentFile, 'open_for_writing', autospec=True)
@patch.object(ExperimentFile, 'close', autospec=True)
class RecordingPDUTestCase(TestCase):
    
    def setUp(self):
        super(RecordingPDUTestCase, self).setUp()
        connect('recording_pdu_test_experiments')
        Experiment.objects.all().delete()

    @attr('unit')
    def test_no_active(self, close_mock, open_mock, put_mock):
        e = Experiment(file = 'file2.txt',
                       since = datetime.now(),
                       name = 'test1')
        e.active = False        
        e.save()
        pdu = RecordingPDU()
        pdu.process_message({'id': 1})
        pdu.process_message({'id': 1})
        
        eq_(0, close_mock.call_count, "no calls expected!")
        eq_(0, open_mock.call_count, "no calls expected!")
        eq_(0, put_mock.call_count, "no calls expected!")

    @attr('unit')
    def test_two_in_parallel(self, close_mock, open_mock, put_mock):
        Experiment(file = 'file1.txt', 
                   since = datetime.now(), 
                   filters = {'type': '1'},
                   name = 'test2').save()
                   
        Experiment(file = 'file2.txt', 
                   since = datetime.now(), 
                   filters = {'type': '2'},
                   name = 'test3').save()
        
        pdu = RecordingPDU()
        pdu.process_message({'type': '3', 'id': '0'})
        pdu.process_message({'type': '1', 'id': '1'})
        pdu.process_message({'type': '2', 'id': '2'})
        pdu.process_message({'type': '1', 'id': '3'})
        pdu.process_message({'type': '2', 'id': '4'})
        pdu.process_message({'type': '3', 'id': '5'})
        
        eq_(2, open_mock.call_count, "2 open expected!")
        open_mock.assert_any_call(_ExperimentFileMatcher("file1.txt"))
        open_mock.assert_any_call(_ExperimentFileMatcher("file2.txt"))
        
        eq_(4, put_mock.call_count, "2 put expected!")
        put_mock.assert_any_call(_ExperimentFileMatcher("file1.txt"),
                                  _MessageMatches('1'))
        put_mock.assert_any_call(_ExperimentFileMatcher("file2.txt"), 
                                 _MessageMatches('2'))
        
    @attr('unit')
    def test_closes_not_active(self, close_mock, open_mock, put_mock):
        Experiment(file = 'file1.txt', 
                   since = datetime.now(), 
                   filters = {'type': '1'},
                   name = 'test4').save()
                   
        e2 = Experiment(file = 'file2.txt', 
                   since = datetime.now(), 
                   filters = {'type': '2'},
                   name = 'test5').save()
        
        RecordingPDU.FILES_PURGE_THRESHOLD = 0.1
        pdu = RecordingPDU()
        pdu.process_message({'type': '3', 'id': '0'})
        pdu.process_message({'type': '1', 'id': '1'})
        pdu.process_message({'type': '2', 'id': '2'})
        
        e2.active = False
        e2.save()
        time.sleep(0.3)
        
        pdu.process_message({'type': '1', 'id': '3'})
        pdu.process_message({'type': '2', 'id': '4'})
        pdu.process_message({'type': '3', 'id': '5'})
                
        eq_(3, put_mock.call_count, "2 put expected!")
        put_mock.assert_any_call(_ExperimentFileMatcher("file1.txt"), 
                                 _MessageMatches('1'))
        put_mock.assert_any_call(_ExperimentFileMatcher("file2.txt"), 
                                 _MessageMatches('2'))
        
        eq_(1, close_mock.call_count, "1 close expected!")
        close_mock.assert_called_once_with(_ExperimentFileMatcher("file2.txt"))
    
    def tearDown(self):
        super(RecordingPDUTestCase, self).tearDown()
        
class _MessageMatches(object):
    def __init__(self, tip):
        self._type = tip
        
    def __eq__(self, other):
        return self._type == other['type']

class _ExperimentFileMatcher(object):
    def __init__(self, efile):
        self._efile = efile
        
    def __eq__(self, other):
        return self._efile == other.fname

