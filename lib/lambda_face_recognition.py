from os import listdir
from pprint import pprint

import unirest

ADD_IMAGE_TO_ALBUM_ENDPOINT = "https://lambda-face-recognition.p.mashape.com/album_train"
RECOGNIZE_IMAGE_ENDPOINT = "https://lambda-face-recognition.p.mashape.com/recognize"

AUTH_PARAMS = {"X-Mashape-Authorization": "4UxoNcB1kMcz7m3CGrrNUDgPWiVhXRcK"}
ANDREI_FOLDER = "/home/diana/ami/AmI-Platform/face_samples/andrei/"
DIANA_FOLDER = "/home/diana/ami/AmI-Platform/face_samples/diana/"
TEST_FOLDER = "/home/diana/ami/AmI-Platform/face_samples/test/"

ALBUM_PARAMS = {"album": "TRAININGSET",
                "albumkey": "804dbad2d1d25af2babe8d3ad129ea6b945990d9e525fe1a43a43af3f4fa0586",
                "urls": ""}

""" HOW TO ADD IMAGES TO ALBUM """

"""
ALBUM_PARAMS['entryid'] = "andrei"
for image in listdir(ANDREI_FOLDER):
    ALBUM_PARAMS['files'] = open(ANDREI_FOLDER + image, mode="r")
    response = unirest.post(ADD_IMAGE_TO_ALBUM_ENDPOINT, AUTH_PARAMS, ALBUM_PARAMS)
    print(response._code)
    pprint(response._body)

ALBUM_PARAMS['entryid'] = "diana"
for image in listdir(DIANA_FOLDER):
    ALBUM_PARAMS['files'] = open(DIANA_FOLDER + image, mode="r")
    response = unirest.post(ADD_IMAGE_TO_ALBUM_ENDPOINT, AUTH_PARAMS, ALBUM_PARAMS)
    print(response._code)
    pprint(response._body)
"""

"""Response Example"""

"""
{u'album': u'TRAININGSET',
 u'entryid': u'andrei',
 u'image_count': 14,
 u'rebuild': False}

{u'album': u'TRAININGSET',
 u'entryid': u'diana',
 u'image_count': 8,
 u'rebuild': False}

"""

""" HOW TO RECOGNIZE AN IMAGE """

"""
test_image = open(TEST_FOLDER + "7f1a13e0-4c16-4dd6-a2cf-09b06f7c0874.jpg", mode="r")
test_image = open(TEST_FOLDER + "d455a677-e122-46b1-96c3-0b4cc5e8d657.jpg", mode="r")
ALBUM_PARAMS["files"] = test_image

response = unirest.post(RECOGNIZE_IMAGE_ENDPOINT, AUTH_PARAMS, ALBUM_PARAMS)
print response._code
pprint(response._body)
"""

"""Response Example"""
"""
{u'images': [u'http://api.lambdal.com/static/uploads/imgGSu_RO.jpg'],
 u'photos': [{u'height': 224,
              u'tags': [{u'attributes': [{u'confidence': 0.21,
                                          u'smile_rating': 0.21,
                                          u'smiling': False},
                                         {u'confidence': 0.8311418625566355,
                                          u'gender': u'male'}],
                         u'center': {u'x': 111, u'y': 111},
                         u'confidence': 0.978945010372561,
                         u'eye_right': {u'x': 95, u'y': 97},
                         u'height': 92,
                         u'mouth_center': {u'x': 108.5, u'y': 142.5},
                         u'mouth_left': {u'x': 88.0, u'y': 142.5},
                         u'mouth_right': {u'x': 129.0, u'y': 142.5},
                         u'nose': {u'x': 104, u'y': 125},
                         u'tid': u'31337',
                         u'width': 92}],
              u'url': u'http://api.lambdal.com/static/uploads/imgGSu_RO.jpg',
              u'width': 224}],
 u'status': u'success'}

{u'images': [u'http://api.lambdal.com/static/uploads/imgIF026n.jpg'],
 u'photos': [{u'height': 248,
              u'tags': [{u'attributes': [{u'confidence': 0.0,
                                          u'smile_rating': 0.0,
                                          u'smiling': False},
                                         {u'confidence': 0.7365683705812067,
                                          u'gender': u'male'}],
                         u'center': {u'x': 124, u'y': 125},
                         u'confidence': 0.978945010372561,
                         u'eye_left': {u'x': 145, u'y': 109},
                         u'eye_right': {u'x': 101, u'y': 111},
                         u'height': 136,
                         u'mouth_center': {u'x': 118.5, u'y': 167.5},
                         u'mouth_left': {u'x': 98.0, u'y': 167.5},
                         u'mouth_right': {u'x': 139.0, u'y': 167.5},
                         u'nose': {u'x': 120, u'y': 147},
                         u'tid': u'31337',
                         u'width': 136}],
              u'url': u'http://api.lambdal.com/static/uploads/imgIF026n.jpg',
              u'width': 248}],
 u'status': u'success'}
"""

