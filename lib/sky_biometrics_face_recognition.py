from os import listdir
from pprint import pprint
import requests

from sky_biometrics.face_client import FaceClient

API_KEY = '711d297cb9a04301a97ef06d33916fae'
API_SECRET = '3c989bc2209e47f2aecba4ef116cec58'

NAMESPACE = 'amilab-test2'
LABELS = {'andrei': 'Andrei Ismail',
          'diana': 'Diana Tatu'}

PREFIX_URL = "https://raw.github.com/ami-lab/AmI-Platform/f6f36c26c2ce29ddec8b714f9650bf9ea7e40149/face_samples/{person_name}@amilab.ro/"
TRAIN_FOLDER = "/home/diana/ami/AmI-Platform/face_samples/train/{person_name}/"
TEST_FOLDER = "/home/diana/ami/AmI-Platform/face_samples/test/{person_name}/"

CHUNK_SIZE = 5

client = FaceClient(API_KEY, API_SECRET)

# Training step
tids = {}
for person_name in ['andrei', 'diana']:
    # Train namespace with person's face samples
    face_samples = []

    for image in listdir(TRAIN_FOLDER.format(person_name=person_name)):
        image_url = "%s%s" % (PREFIX_URL.format(person_name=person_name), image)
        response = requests.get(image_url)
        if response.status_code == 200:
            face_samples.append(image_url)

    # Split face samples in smaller chunks to avoid Exception responses from
    # SkyBiometrics API.
    chunks = []
    chunk_count = len(face_samples) / CHUNK_SIZE
    for i in range(0, chunk_count):
        chunk = []
        for j in range(CHUNK_SIZE * i, CHUNK_SIZE * (i + 1)):
            chunk.append(face_samples[j])
        chunks.append(chunk)

    for chunk in chunks:
        chunk = ','.join(chunk)

        print("Detecting faces for %s..." % person_name)
        response = client.faces_detect(chunk, aggressive=True)
        pprint(response)

        print("Saving tags for %s..." % person_name)
        tids[person_name] = [photo['tags'][0]['tid']
                             for photo in response['photos']
                             if len(photo.get('tags', [])) > 0 and
                             len(photo['tags'][0].get('tid'))]
        client.tags_save(tids=',' . join(tids[person_name]),
                         uid='%s@%s' % (person_name, NAMESPACE),
                         label=LABELS[person_name])
        pprint(response)

        print("Training set for %s" % person_name)
        response = client.faces_train('%s@%s' % (person_name, NAMESPACE))
        pprint(response)


# Testing step
for person_name in ['andrei', 'diana']:
    face_samples = []

    for image in listdir(TEST_FOLDER.format(person_name=person_name)):
        image_url = "%s%s" % (PREFIX_URL.format(person_name=person_name), image)
        face_samples.append(image_url)

    face_samples = ','.join(face_samples)

    print("Recognizing %s..." % person_name)
    response = client.faces_recognize('all', face_samples, namespace=NAMESPACE)

    print("Results for %s sample:" % person_name)
    pprint(response['photos'][0]['tags'][0]['uids'])
