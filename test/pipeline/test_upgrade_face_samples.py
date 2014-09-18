import os
from unittest import TestCase

from mock import patch, ANY
from nose.plugins.attrib import attr
from nose.tools import ok_

from pybetaface.api import BetaFaceAPI
from pipeline.upgrade_face_samples import UpgradeFaceSamples
from factories import UpgradeFaceSamplesFactory


def set_field(self, field, val):
        print "%s = %s" % (field, val)
        setattr(self, field, val)
        return None


def raise_(e):
    raise e


class TestUpgradeFaceSamplesTest(TestCase):

    @attr('integration')
    @patch.object(UpgradeFaceSamples, 'save_image_to_file')
    @patch.object(BetaFaceAPI, 'upload_face', )
    @patch.object(os, 'remove')
    def test_pdu_calls_betaface_api_with_correct_params(self, _, api_upload_image, image_save):
        pdu = UpgradeFaceSamples()

        # Init message
        message = UpgradeFaceSamplesFactory()

        # Validate message
        ok_(pdu.validate_message(message), "Message is valid")

        # Call tested methods
        pdu.process_message(message)

        image_save.assert_called_once_with(message['head_image']['image'],
                                           message['head_image']['width'],
                                           message['head_image']['height'],
                                           ANY)
        path = image_save.call_args_list[0][0][3]
        api_upload_image.assert_called_once_with(path, message['person_name'])

    @attr('integration')
    @patch.object(UpgradeFaceSamples, 'save_image_to_file')
    @patch.object(BetaFaceAPI, 'upload_face', )
    @patch.object(os, 'remove')
    def test_save_image_before_upload(self, _, api_upload_image, image_save):
        # Check if upload image is called after saving image to file.
        # If not, an exception will be raised.
        image_save.side_effect = (
            lambda *_: setattr(self, 'called_upload', True))

        api_upload_image.side_effect = (
            lambda *_:
                raise_(Exception()) if not getattr(self, 'called_upload', False)
                else None)

        pdu = UpgradeFaceSamples()

        # Init message
        message = UpgradeFaceSamplesFactory()
        pdu.process_message(message)
