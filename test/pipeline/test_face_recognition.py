import logging
import time
from unittest import TestCase

from mock import patch

from lib import log
from lib.session_store import SessionStore
from core.constants import MATCHES_MOCK
from factories import FaceRecognitionFactory
from pipeline import face_recognition
from pipeline.face_recognition import FaceRecognition

MAX_WAIT = 5


class TestFaceRecognition(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestFaceRecognition, cls).setUpClass()
        log.setup_logging(level=logging.DEBUG)

    @patch.object(SessionStore, 'set')
    def test_send_message_to_redis_recognized_face(self, session_store_mock):
        orig_fn = face_recognition.skybiometry_recognition
        face_recognition.skybiometry_recognition = get_matches

        pdu = FaceRecognition(debug=True)
        message = FaceRecognitionFactory()
        pdu.process_message(message)
        time.sleep(MAX_WAIT)

        sid = message['session_id']
        t = 0
        max_probability = max(MATCHES_MOCK.values())
        person_name = MATCHES_MOCK.keys()[MATCHES_MOCK.values(
            ).index(max_probability)]
        info = {'person_name':  person_name}

        session_store_mock.assert_called_once_with(sid, t, info)
        face_recognition.skybiometry_recognition = orig_fn


def get_matches(_):
    return MATCHES_MOCK
