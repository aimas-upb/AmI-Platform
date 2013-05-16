from mock import patch
from unittest import TestCase

from lib.session_store import SessionStore
from pipeline.dashboard import Dashboard
from test.pipeline.messages import MEASUREMENTS_MESSAGE_IMAGE_RGB


class TestDashboard(TestCase):

    @patch.object(SessionStore, "set")
    def test_send_message_to_redis_when_session_id(self, session_store_mock):
        pdu = Dashboard()
        message = MEASUREMENTS_MESSAGE_IMAGE_RGB
        pdu.process_message(message)
        sid = message['session_id']
        time = message['created_at']
        mappings = {'image_rgb': message['image_rgb']}
        session_store_mock.assert_called_once_with(sid, time, mappings)
