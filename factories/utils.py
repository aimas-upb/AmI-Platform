import base64
from math import pi as PI
import os
from random import uniform, randrange


def get_random_image(width, height):
    """Returns a random width x height image base64 encoded."""
    return base64.b64encode(os.urandom(height * width * 3))

def get_random_hash(length):
    """Returns a random has of a given length."""
    return os.urandom(length).encode('hex')


def get_random_skeleton():
    return {}


def get_random_2D_skeleton():
    return {}


def get_random_3D_skeleton():
    return {}


def get_random_angle():
    return uniform(-PI, PI)


def get_random_sensor_position():
    """Returns a random position of a sensor."""
    return {"beta": get_random_angle(),
            "alpha": get_random_angle(),
            "gamma": get_random_angle(),
            "X": randrange(0, 10000),
            "Y": randrange(0, 10000),
            "Z": randrange(0, 10000)
            }
