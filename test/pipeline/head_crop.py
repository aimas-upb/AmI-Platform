from unittest import TestCase

from bson import ObjectId
import pymongo

from pipeline.head_crop import HeadCrop

class HeadCropTest(TestCase):
    
    def setUp(self):
        mongo_connection = pymongo.Connection()
        self.image = mongo_connection.measurements.docs.find_one(ObjectId('50b5cbb9618e370890cda0b8'))
        self.skeleton = mongo_connection.measurements.docs.find_one(ObjectId('50b5cbbb618e370890cda0bb'))
   
    def test_head_crop_doesnt_crash_on_skeleton_image(self):
        head_crop = HeadCrop()
        head_crop.process_message(self.skeleton)
        head_crop.process_message(self.image)
        
    def test_head_crop_doesnt_crash_on_image_skeleton(self):
        head_crop = HeadCrop()
        head_crop.process_message(self.image)
        head_crop.process_message(self.skeleton)
        