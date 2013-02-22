OPENNI
===========

In NITE versions before 1.5, the user had to stand in a calibration (“psi”) pose
before the system could build his skeleton. Now the skeleton can be created shortly
after the user enters the scene.

To enable this for 1.5.4 version, create 
	/usr/etc/primesense/Features_1_5_4/FeatureExtraction.ini

with the following settings:
	[FeatureExtractor]
	AlwaysRunCalibration=1
	AutoBodyParameters=1
	UseAutoCalibration=1
	
	[Generator]
	;Preference=Quality
	Preference=Speed


Limitations
===========
	- Auto calibration works on standing users. A sitting user will not be 
		calibrated automatically.
	- Most of the user‟s body should be visible in order for the automatic 
		calibration to take place.
	- The user should be located further than ~1m from the sensor in order 
		for the automatic calibration to start.


Recommendations
===========
The following recommendations will help to complete the calibration faster 
and achieve better results. 
The recommendations apply to the auto-calibration phase only (first
seconds of the user in the scene) and not to the subsequent frames.
	- The user should be facing the sensor and standing upright.
	- The hands should not hide the torso area.
	- The user should avoid fast motion


