#!/bin/bash
KINECT_SERIAL=$AMI_SENSOR_KINECT_SERIAL_1
if [ -n $KINECT_SERIAL  ]
then
    parts=(`lsusb -v -d 045e:02ae | grep -e "Bus\|iSerial" | grep -B 1 $KINECT_SERIAL | head -n1 | cut -d' ' -f2,4 | cut -d':' -f1`)
    bus=$(echo ${parts[0]} | sed 's/^0*//')
    device=$(echo ${parts[1]} | sed 's/^0*//')
    `dirname $0`/Bin/x64-Release/Sample-NiUserTracker $KINECT_SERIAL $bus $device
else
    `dirname $0`/Bin/x64-Release/Sample-NiUserTracker
fi
