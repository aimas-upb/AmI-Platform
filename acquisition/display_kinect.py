'''
    Script that takes some images (Kinect depth maps) from a Kestrel queue and 
    displays them using OpenCV.
'''
import kestrel
import pickle
import cv2

kestrel_client = kestrel.Client(['1141.85.159.129:10153'])

while True:
    img = kestrel_client.get('ami53', 10)
    if img is None:
        continue

    img = json.loads(img)
    cv2.namedWindow("Kinect Depth Map")

