#!/bin/bash
KINECT_SERIAL=$1
echo Starting with serial -$KINECT_SERIAL-
if [ -z $KINECT_SERIAL  ]
then
     `dirname $0`/Bin/x64-Release/Sample-NiUserTracker
else
    parts=(`lsusb -v -d 045e:02ae | grep -e "Bus\|iSerial" | grep -B 1 $KINECT_SERIAL | head -n1 | cut -d' ' -f2,4 | cut -d':' -f1`)
    bus=$(echo ${parts[0]} | sed 's/^0*//')
    device=$(echo ${parts[1]} | sed 's/^0*//')
    `dirname $0`/Bin/x64-Release/Sample-NiUserTracker $KINECT_SERIAL $bus $device
fi
