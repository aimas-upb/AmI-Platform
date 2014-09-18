import json
import logging

from nose.plugins.attrib import attr
from nose.tools import eq_

from core import PipelineTest
from dummy_pdu import DummyPDU
from dummy_measurements_player import DummyMeasurementsPlayer

logger = logging.getLogger(__name__)


class TestPipelineTest(PipelineTest):

    DELAY_UNTIL_MESSAGES_PROPAGATE = 1.0
    PDUs = [DummyPDU]

    def _measurements_player_instance(self, data_file, callback):
        harcoded_msgs = [{'a': 'b'}, {'c': 'd'}]
        return DummyMeasurementsPlayer(data_file=data_file,
                                       callback=callback,
                                       hardcoded_msgs=harcoded_msgs)

    @attr('unit', 'pipeline')
    def test_that_pipeline_test_works_ok(self):
        self._test_pipeline()

    def check_results(self):
        m1 = json.loads(self._queue_system.get('dummy'))
        eq_(m1, {'a': 'b'}, 'm1 should have correct value')

        m2 = json.loads(self._queue_system.get('dummy'))
        eq_(m2, {'c': 'd'}, 'm2 should have correct value')
