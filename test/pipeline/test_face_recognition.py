import logging
import time
from unittest import TestCase

from mock import patch

from lib import log
from lib.sessions_store import SessionsStore
from messages import MATCHES_MOCK, FACE_RECOGNITION_SAMPLE_MESSAGE
from pipeline.face_recognition import FaceRecognition

MAX_WAIT = 5


class TestFaceRecognition(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super(TestFaceRecognition, cls).setUpClass()
        log.setup_logging(level=logging.DEBUG)

    @patch.object(SessionsStore, 'set')
    def test_send_message_to_redis_recognized_face(self, sessions_store_mock):
        from pipeline import face_recognition
        orig_fn = face_recognition.betaface_recognition
        face_recognition.betaface_recognition = get_matches

        pdu = FaceRecognition()
        pdu.process_message(FACE_RECOGNITION_SAMPLE_MESSAGE)
        time.sleep(MAX_WAIT)

        sid = FACE_RECOGNITION_SAMPLE_MESSAGE['session_id']
        t = FACE_RECOGNITION_SAMPLE_MESSAGE['created_at']
        max_probability = max(MATCHES_MOCK.values())
        person_name = MATCHES_MOCK.keys()[MATCHES_MOCK.values(
            ).index(max_probability)]
        info = {'person_name':  person_name}

        sessions_store_mock.assert_called_once_with(sid, t, info)
        face_recognition.betaface_recognition = orig_fn

def get_matches(image_dict):
    return MATCHES_MOCK