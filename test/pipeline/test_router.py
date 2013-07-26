import unittest
from mock import patch

from factories import RouterFactory, utils
from models.experiment import Experiment
from pipeline.router import Router
from testutils.matcher import Matcher


class RouterTest(unittest.TestCase):

    @patch.object(Router, 'send_to')
    @patch.object(Experiment, 'get_active_experiments')
    def test_routes_to_experiments(self, active_experiments_mock, send_to_mock):
        """Assert that a message is forwarded 'recorder' if Router receives a
        message when there are active experiments going on.
        """
        router = Router()
        messages = [RouterFactory('image_rgb') for _ in range(3)]
        active_experiments_mock.return_value = messages

        for m in messages:
            m.update({'id': utils.get_random_hash(1)})
            router.process_message(m)

        for m in messages:
            send_to_mock.assert_any_call(Matcher('recorder', lambda o: o),
                                         Matcher(m['id'], lambda o: o['id']))
