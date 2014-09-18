#!/bin/bash
su -c "DISPLAY=:0 /home/ami/AmI-Platform/acquisition/kinect/kinect-acq-wrapper.sh $AMI_SENSOR_KINECT_SERIAL_1 2>&1" ami
