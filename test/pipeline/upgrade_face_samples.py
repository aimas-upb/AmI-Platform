import time
from unittest import TestCase

from mock import patch, ANY
from nose.tools import ok_, eq_

from pipeline.upgrade_face_samples import UpgradeFaceSamples
from pipeline.upgrade_face_samples import BetaFaceAPI

def set_field(self, field, val):
        print "%s = %s" % (field, val)
        setattr(self, field, val)
        return None
    
def raise_(e):
    raise e
    

class UpgradeFaceSamplesTest(TestCase):

    @patch.object(UpgradeFaceSamples, 'save_image_to_file')
    @patch.object(BetaFaceAPI, 'upload_face')
    def test_pdu_calls_betaface_api_with_correct_params(self, api_upload_image, image_save):
        pdu = UpgradeFaceSamples()
        
        # init message
        message = {
            'person_name': 'diana@amilab.ro',
            'head_image': {
                'image': 'ABCDEF',
                'width': 640,
                'height': 480
            }
        }
        
        # validate message
        ok_(pdu.validate_message(message), "Message is valid")
        
        # call tested methods
        pdu.process_message(message)

        image_save.assert_called_once_with(message['head_image']['image'], 
                                           message['head_image']['width'], 
                                           message['head_image']['height'], 
                                           ANY)
        path = image_save.call_args_list[0][0][3]
        api_upload_image.assert_called_once_with(path, message['person_name'])
        
    
    @patch.object(UpgradeFaceSamples, 'save_image_to_file')
    @patch.object(BetaFaceAPI, 'upload_face', )
    def test_save_image_before_upload(self, api_upload_image, image_save):
        # check if upload image is called after saving image to file
        # if not, an exception will be raised
        image_save.side_effect = (lambda *kwargs: setattr(self, 'called_upload', True))
        api_upload_image.side_effect = (lambda *kwargs: raise_(Exception()) if not getattr(self, 'called_upload', False) else None )
        
        pdu = UpgradeFaceSamples()
        
        message = {
            'person_name': 'diana@amilab.ro',
            'head_image': {
                'image': 'ABCDEF',
                'width': 640,
                'height': 480
            }
        }
        
        pdu.process_message(message)