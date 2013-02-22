import unittest
from pipeline.router import Router
from mock import patch
from testutils.matcher import Matcher

class RouterTest(unittest.TestCase):

    @patch.object(Router, 'send_to')
    def test_routes_to_experiments(self, send_to_mock):
        router = Router()
        messages = [{'id': 'b'}, {'id': 'c'}, {'id': 'd'}]
        
        for m in messages:
            router.process_message(m)
        
        for m in messages:
            send_to_mock.assert_any_call(Matcher('recorder', lambda o: o),
                                         Matcher(m['id'], lambda o: o['id']))
        
