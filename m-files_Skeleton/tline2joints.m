function parts= tline2joints(tline) %#ok<*STOUT>
% function to return the coordinates of the 15 body-parts in a cell-array content
% from a tline-input (string of chars)-resulted from reading a line from a CSV-file (from
% Kinect-reading ; the fields of the 'parts' (the output with the 15 body-joints
% are in the order as it follows below:
% parts = {'head(1-3)','neck(4-6)','left_shoulder(7-9)','right_shoulder(10-12)',...
%  	'left_elbow(13-15)','right_elbow(16-18)','left_hand(19-21)','right_hand(22-24)', ...
%  	'torso(25-27)','left_hip(28-30)','right_hip(31-33)','left_knee(34-36)',...
%   'right_knee(37-39)','left_foot(40-42)','right_foot(43-45)'};
x = str2num(tline); clear tline; %#ok<*ST2NM> % convert from chars-array to floats
         head_x= x(1,1); head_y= x(1,2); head_z= x(1,3);
         neck_x= x(1,4); neck_y= x(1,5); neck_z= x(1,6);
         left_shoulder_x= x(1,7); left_shoulder_y= x(1,8); left_shoulder_z= x(1,9);
         right_shoulder_x= x(1,10); right_shoulder_y= x(1,11); right_shoulder_z= x(1,12);
         left_elbow_x= x(1,13); left_elbow_y= x(1,14); left_elbow_z= x(1,15);
         right_elbow_x= x(1,16); right_elbow_y= x(1,17); right_elbow_z= x(1,18);
         left_hand_x= x(1,19); left_hand_y= x(1,20); left_hand_z= x(1,21);
         right_hand_x= x(1,22); right_hand_y= x(1,23); right_hand_z= x(1,24);
         torso_x= x(1,25); torso_y= x(1,26); torso_z= x(1,27);
         left_hip_x= x(1,28); left_hip_y= x(1,29); left_hip_z= x(1,30);
         right_hip_x= x(1,31); right_hip_y= x(1,32); right_hip_z= x(1,33);
         left_knee_x= x(1,34); left_knee_y= x(1,35); left_knee_z= x(1,36);
         right_knee_x= x(1,37); right_knee_y= x(1,38); right_knee_z= x(1,39);
         left_foot_x= x(1,40); left_foot_y= x(1,41); left_foot_z= x(1,42);
         right_foot_x= x(1,43); right_foot_y= x(1,44); right_foot_z= x(1,45);
   parts{1,1}=head_x;  parts{1,2}=head_y; parts{1,3}=head_z;
   parts{1,4}=neck_x;  parts{1,5}=neck_y; parts{1,6}=neck_z;
   parts{1,7}=left_shoulder_x;  parts{1,8}=left_shoulder_y; parts{1,9}=left_shoulder_z;
   parts{1,10}=right_shoulder_x;  parts{1,11}=right_shoulder_y; parts{1,12}=right_shoulder_z;      
   parts{1,13}=left_elbow_x;  parts{1,14}=left_elbow_y; parts{1,15}=left_elbow_z;
   parts{1,16}=right_elbow_x;  parts{1,17}=right_elbow_y; parts{1,18}=right_elbow_z;
   parts{1,19}=left_hand_x;  parts{1,20}=left_hand_y; parts{1,21}=left_hand_z;
   parts{1,22}=right_hand_x;  parts{1,23}=right_hand_y; parts{1,24}=right_hand_z;
   parts{1,25}=torso_x;  parts{1,26}=torso_y; parts{1,27}=torso_z;
   parts{1,28}=left_hip_x;  parts{1,29}=left_hip_y; parts{1,30}=left_hip_z;
   parts{1,31}=right_hip_x;  parts{1,32}=right_hip_y; parts{1,33}=right_hip_z;
   parts{1,34}=left_knee_x;  parts{1,35}=left_knee_y; parts{1,36}=left_knee_z;   
   parts{1,37}=right_knee_x;  parts{1,38}=right_knee_y; parts{1,39}=right_knee_z;
   parts{1,40}=left_foot_x;  parts{1,41}=left_foot_y; parts{1,42}=left_foot_z;   
   parts{1,43}=right_foot_x;  parts{1,44}=right_foot_y; parts{1,45}=right_foot_z;         
                     