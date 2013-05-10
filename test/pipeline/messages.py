
MEASUREMENTS_MESSAGE_SKELETON = {
    "skeleton_2D" : {
        "head" : {
            "Y" : 172.24,
            "X" : 349.14
        },
        "neck" : {
            "Y" : 404.42,
            "X" : 373.8
        },
        "left_shoulder" : {
            "Y" : 452.77,
            "X" : 219.91
        },
        "left_hand" : {
            "Y" : 658.1,
            "X" : 227.06
        },
        "left_knee" : {
            "Y" : 876.71,
            "X" : 354.5
        },
        "right_elbow" : {
            "Y" : 428.03,
            "X" : 400.99
        },
        "right_shoulder" : {
            "Y" : 361.81,
            "X" : 509.45
        },
        "right_hand" : {
            "Y" : 417.75,
            "X" : 541.41
        },
        "left_hip" : {
            "Y" : 642.4,
            "X" : 367.61
        },
        "right_hip" : {
            "Y" : 604,
            "X" : 459.71
        },
        "left_foot" : {
            "Y" : 1118.87,
            "X" : 349.48
        },
        "left_elbow" : {
            "Y" : 604.2,
            "X" : 229.36
        },
        "torso" : {
            "Y" : 518.64,
            "X" : 395.14
        },
        "right_knee" : {
            "Y" : 819.31,
            "X" : 488.49
        },
        "right_foot" : {
            "Y" : 1004.28,
            "X" : 424.23
        }
    },
    "sensor_id" : "daq-05",
    "created_at" : 1362756593,
    "player" : "9",
    "sensor_type" : "kinect",
    "context" : "default",
    "type" : "skeleton",
    "skeleton_3D" : {
        "head" : {
            "Y" : 472.58,
            "X" : -431.54,
            "Z" : 1708.65
        },
        "neck" : {
            "Y" : 141.08,
            "X" : -372.38,
            "Z" : 1611
        },
        "left_shoulder" : {
            "Y" : 72.79,
            "X" : -550.64,
            "Z" : 1509.54
        },
        "left_hand" : {
            "Y" : -215.97,
            "X" : -651.09,
            "Z" : 1815.79
        },
        "left_knee" : {
            "Y" : -526.49,
            "X" : -439.62,
            "Z" : 1773.33
        },
        "right_elbow" : {
            "Y" : 124.14,
            "X" : -376.93,
            "Z" : 1816.13
        },
        "right_shoulder" : {
            "Y" : 209.38,
            "X" : -194.12,
            "Z" : 1712.45
        },
        "right_hand" : {
            "Y" : 136.9,
            "X" : -152.75,
            "Z" : 1784.27
        },
        "left_hip" : {
            "Y" : -183.67,
            "X" : -409.24,
            "Z" : 1730.21
        },
        "right_hip" : {
            "Y" : -134.99,
            "X" : -282.19,
            "Z" : 1802.52
        },
        "left_foot" : {
            "Y" : -857.99,
            "X" : -438.11,
            "Z" : 1736.7
        },
        "left_elbow" : {
            "Y" : -121.79,
            "X" : -578.59,
            "Z" : 1622.64
        },
        "torso" : {
            "Y" : -9.13,
            "X" : -359.05,
            "Z" : 1688.68
        },
        "right_knee" : {
            "Y" : -470.83,
            "X" : -247.6,
            "Z" : 1882.05
        },
        "right_foot" : {
            "Y" : -777.87,
            "X" : -363.68,
            "Z" : 1941.05
        }
    },
    "sensor_position" : {
        "beta" : 0,
        "X" : 0,
        "Y" : 0,
        "alpha" : 0,
        "Z" : 0,
        "gamma" : 0
    }
}

MEASUREMENTS_MESSAGE_IMAGE_RGB = {
    "sensor_id": "daq-04",
    "session_id": "daq-04_1_0123456789ABCDEF",
    "inserted_at": "1366974705000",
    "image_rgb": {"width": 1280,
                  "image": "ABCDE",
                  "height": 1024},
    "sensor_type": "kinect",
    "context": "default",
    "type": "image_rgb",
    "created_at": 1366974699,
    "sensor_position": {"beta": 0.3665,
                        "alpha": -1.5708,
                        "gamma": 0,
                        "X": 9340,
                        "Y": 2299,
                        "Z": 1009},
}

MATCHES_MOCK = {
                'diana@amilab.ro': 0.879,
                'andrei@amilab.ro': 0.354
                }

FACE_RECOGNITION_SAMPLE_MESSAGE = {
    'head_image': {
                   'image': 'A' * (640 * 480 * 3 * 4/3),
                   'width':640,
                   'height': 480,
                   },
    'session_id': 'daq-04_1_0123456789ABCDEF',
    'created_at': 1366974699,
    }
