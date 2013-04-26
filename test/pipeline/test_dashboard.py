from mock import patch
from unittest import TestCase

from lib.sessions_store import SessionsStore
from pipeline.dashboard import Dashboard
from test.pipeline.messages import MEASUREMENTS_MESSAGE_IMAGE_RGB


class TestDashboard(TestCase):

    @patch.object(SessionsStore, "set")
    def test_send_message_to_redis_when_session_id(self, sessions_store_mock):
        pdu = Dashboard()
        message = MEASUREMENTS_MESSAGE_IMAGE_RGB
        pdu.process_message(message)
        sid = message['session_id']
        time = message['created_at']
        sessions_store_mock.assert_called_once_with(sid, time, None)
