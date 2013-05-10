AmI-Platform
============

Environment variables in order to configure a node:

AMI_KESTREL_SERVER_IP  - defaults to "127.0.0.1"
AMI_KESTREL_SERVER_PORT - defaults to "22133"
AMI_SENSOR_ID - defaults to "anonymous"



1. Kestrel Queues Diagram
============

<insert diagram here>



2. Queues
============
```python
‘measurements’ (DataAcquisition → Router)
	{
		'context': 'default', 		// context’s name - used by Mr. Vladutu for
						// stuff like "standing_down", etc.
		'sensor_type': 'kinect', 	// can also be 'arduino', 'sony360ptz'
		'sensor_id': '23',		// unique id of device -hardcoded currently
						// (will be command param)
		'sensor_position': {
			'x': 23, 'y': 42, 'z': 87
		},
		'type': {'skeleton'}		// can also be: 'image_depth', 'image_rgb'
		'image_rgb': {			// base64-encoded array of 3 * width * height bytes
			'image': 'AAAA',
			'width': 640,
			'height': 480
		},
		'image_depth': {		// base64-encoded array of 3 * width * height bytes
			'image': 'BBBB',
			'width': 640,
			'height': 480
		},
		'skeleton_2D': {		// JSON with skeleton coordinates. Kinect-specific field
			'head': { 'x': 23, 'y': 42 },
			'neck': { 'x': 27, 'y': 55 	},
			…
		},
		'skeleton_3D': {		// JSON with skeleton coordinates. Kinect-specific field
			'head': { 'x': 23, 'y': 42, 'z': 87 },
			'neck': { 'x': 27, 'y': 55, 'z': 87 },
			…
	},
}

‘mongo-writer’ (Router → MongoDB)
	-- same as ‘measurements’ queue message format

‘mongo-writer’ (RoomPosition → MongoDB)
	{
       	'type': 'subject_position',
              'sensor_id': message['sensor_id'],
              'created_at': message['created_at'],
              'X': pos[0,0],
              'Y': pos[1,0],
              'Z': pos[2,0],
      	}

‘head-crop’ (Router → HeadCrop)
	-- same as ‘measurements’ queue message format

‘room-position’ (Router → RoomPosition)
	-- same as ‘measurements’ queue message format



‘face-recognition’ (HeadCrop → FaceRecognition, FaceDetection → FaceRecognition)
	{
		'head_image': {		// head cropped image 
		'image': 'AAAA',
		'width':640,
		'height': 480
		}

	}

‘face-detection’ (HeadCrop → FaceDetection)
	{
		'image_rgb': {		// face could not be cropped: detect face
		'image': 'AAAA',
		'width':640,
		'height': 480
		}
	}

‘upgrade-face-samples’ (FaceRecognition → UpgradeFaceSamples)
	{
	'head_image': {
		'image': 'AAAA',
		'width':640,
		'height': 480
		},
	'person_name': 'andrei@amilab.ro'
	}

‘room’ (FaceRecognition → Room)
	{
		'person_name': 'andrei@amilab.ro',
		'event_type': 'person_appeared'
	}

‘ip-power’ (Room → IPPower)
	{
		'cmd': 'on',
	       	'ip': '192.168.0.30',
	       	'output': '1',
	}


‘text-to-speech’ (Room → TextToSpeech)
	{
		'text': 'Hello, Andrei!'
	}
```



