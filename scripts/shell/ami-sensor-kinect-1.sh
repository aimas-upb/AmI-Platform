#!/bin/bash
echo test $AMI_SENSOR_KINECT_SERIAL_1 $AMI_KESTREL_SERVER_IP > /tmp/x.txt
su -c "DISPLAY=:0 /home/ami/AmI-Platform/acquisition/kinect/kinect-acq-wrapper.sh $AMI_SENSOR_KINECT_SERIAL_1 2>&1" ami
