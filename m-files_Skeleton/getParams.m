function v = getParams(varargin) 
% Function to compute all features from a line of the CSV (from Kinect skeleton);
%
% These features are to be used by a classifier to assess the body-posture
%  The 4 types of params (features) computed from each line are:
% 1) the angle between any triplet (of interest) of 3D points given by Kinect_Features_Compute(i1,i2,i3)
% 2) the angle of the line (formed by 2 pairs of 3D points) with y0z plane
% both 2) & 3) given by Line_to_Plane_Angle
% 3) the angle of the line (formed by 2 pairs of 3D points) with x0y plane
% 4) the distances between pairs of body-segments  (i.e. vectors) using distBW2lines
% 
%  Needs 2 input parameters: first is the name of the file (e.g.'export-AD_dreapta_sus.csv')
%  Second parameter is the index of the line of the record (in the csv file
%  above), ie the measurement's index

cd E:\new_CSV\CSV-filtrate\; % cd /home/JohnDoe/data/filtered_CSV/;

% The folder where the repository of filtered-CSVs is to be found
% Name of the files in that folder are Like: filename = 'export-AD_dreapta_sus.csv'; 
% listing = dir('*.csv');
% m = size(listing,1); % The Number of filtered records in the analysed folder

[~,n]=size(varargin);
if (n<1) || (n>2)
    disp('Wrong number of input arguments shouldn''t be less than 1 or more than 2!')
    return;
elseif (n == 2),
    disp('2 inputs given')
    disp('The first argument gives the file name, 2nd argument gives the record No.')
    a=  varargin{1};
    LineNum = varargin{2};
elseif (n==1),
    LineNum= 1; % By default I consider the first measurement line
    a=  varargin{1};
end

 clear fileID;   
 fileID = fopen(a); %#ok<*NASGU>
     % Get the 1st line of coordinates:
     C = textscan(fid, '%s','delimiter', '\n'); % Read the whole file in a cell-array
     tline = C{1}{LineNum}; clear C;
     
     sp=find(tline==','); % comma separates coordinates a coord is from idx-->sp(i)-1
      Ncoord=size(sp,2)+1; 
      if mod((Ncoord+1),3)==0, % should be 45 (15 pts *3); checked that:
      
      for j=1:Ncoord,
           parts= tline2joints(tline);
         % parts = {'head(1-3)','neck(4-6)','left_shoulder(7-9)','right_shoulder(10-12)',...
         %  	'left_elbow(13-15)','right_elbow(16-18)','left_hand(19-21)','right_hand(22-24)', ...
         %  	'torso(25-27)','left_hip(28-30)','right_hip(31-33)','left_knee(34-36)',...
         %      'right_knee(37-39)','left_foot(40-42)','right_foot(43-45)'}; 
        
         % Start processing angles of triplets of points (from 'parts' above) && angles of "points pairs with Planes" ...
         % Have to figure out which combinations of doublets/triplets are interesting for the assessment of subject's posture
         %    I. Compute angles of the Triplets of points using Kinect_Features_Compute(i1,i2,i3):
         % T1 	|   head(1-3)               |  		neck(4-6)               | 	left_shoulder(7-9)
         % T2 	|   head(1-3)               |  		neck(4-6)               | 	right_shoulder(10-12)
         % T3 	|  	neck(4-6)               |  		left_shoulder(7-9)      | 	left_elbow(13-15)
         % T4 	|  	neck(4-6)               |  		right_shoulder(10-12)	| 	right_elbow(16-18)
         % T5	|  	left_shoulder(7-9)      | 		left_elbow(13-15) 		|	left_hand(19-21)
         % T6	|  	right_shoulder(10-12)	| 		right_elbow(16-18)      |	right_hand(22-24)
         % T7	|	head(1-3)               |  		neck(4-6)               | 	torso(25-27)
         % T8	|	neck(4-6)               |  		torso(25-27)            | 	left_hip(28-30)
         % T9	|	neck(4-6)               |  		torso(25-27)            | 	right_hip(31-33)
         % T10	| 	torso(25-27)            | 		left_hip(28-30)         |	left_knee(34-36)
         % T11	| 	torso(25-27)            | 		right_hip(31-33)        |	right_knee(37-39)
         % T12	| 	left_hip(28-30)         |		left_knee(34-36)        |   left_foot(40-42)
         % T13	| 	right_hip(31-33)        |		right_knee(37-39)       |   right_foot(43-45)
         % T14	|	neck(4-6)               |  		torso(25-27)            | 	left_knee(34-36)
         % T15	|	neck(4-6)               |  		torso(25-27)            | 	right_knee(37-39)
         %
         i1=0; % i is the index of the body part; i = 0...14; i ==0 (Head), i=1 (Neck)... i=14 (right_foot)
         i2=1; i3=2;
         angl1= Kinect_Features_Compute(parts,i1,i2,i3); clear i1 i2 i3; pause(0.001);
         i1=0; i2=1; i3=3; angl2= Kinect_Features_Compute(parts,i1,i2,i3); clear i1 i2 i3; pause(0.001);
         i1=1; i2=2; i3=4; angl3= Kinect_Features_Compute(parts,i1,i2,i3); clear i1 i2 i3; pause(0.001);
         i1=1; i2=3; i3=5; angl4= Kinect_Features_Compute(parts,i1,i2,i3); clear i1 i2 i3; pause(0.001);
         i1=2; i2=4; i3=6; angl5= Kinect_Features_Compute(parts,i1,i2,i3); clear i1 i2 i3; pause(0.001);
         i1=3; i2=5; i3=7; angl6= Kinect_Features_Compute(parts,i1,i2,i3); clear i1 i2 i3; pause(0.001);
         i1=0; i2=1; i3=8; angl7= Kinect_Features_Compute(parts,i1,i2,i3); clear i1 i2 i3; pause(0.001);
         i1=1; i2=8; i3=9; angl8= Kinect_Features_Compute(parts,i1,i2,i3); clear i1 i2 i3; pause(0.001);
         i1=1; i2=8; i3=10; angl9= Kinect_Features_Compute(parts,i1,i2,i3); clear i1 i2 i3; pause(0.001);
         i1=8; i2=9; i3=11; angl10= Kinect_Features_Compute(parts,i1,i2,i3); clear i1 i2 i3; pause(0.001);
         i1=8; i2=10; i3=12; angl11= Kinect_Features_Compute(parts,i1,i2,i3); clear i1 i2 i3; pause(0.001);
         i1=9; i2=11; i3=13; angl12= Kinect_Features_Compute(parts,i1,i2,i3); clear i1 i2 i3; pause(0.001);
         i1=10; i2=12; i3=14; angl13= Kinect_Features_Compute(parts,i1,i2,i3); clear i1 i2 i3; pause(0.001);
         i1=1; i2=8; i3=11; angl14= Kinect_Features_Compute(parts,i1,i2,i3); clear i1 i2 i3; pause(0.001);
         i1=1; i2=8; i3=12; angl15= Kinect_Features_Compute(parts,i1,i2,i3); clear i1 i2 i3; pause(0.001);
         
         % 	  II. Compute angles from Pairs_of_Points to Planes /distance (using Line_to_Plane_Angle):
         % A. body trunk characteristic tree (MSc-Thesis Diana Tatu, Chpter 3-Architecture.docx)
         % P1	|	neck(4-6)               |  		torso(25-27)            | 		y0z
         % P2	|	neck(4-6)               |  		torso(25-27)            | 		x0y
         i1=1; P1=[parts{1,3*i1+1},parts{1,3*i1+2},parts{1,3*i1+3}];
         i2=8; P2=[parts{1,3*i2+1},parts{1,3*i2+2},parts{1,3*i2+3}];
         angleInDegrees1=Line_to_Plane_Angle(P1,P2,1);
         angleInDegrees2=Line_to_Plane_Angle(P1,P2,2); clear P1 P2;
         
         % B. 	Upper-limbs characteristic trees (using Line_to_Plane_Angle):
         % P1	|	left_shoulder(7-9)      |  		left_elbow(13-15)       | 		y0z
         % P2	|	left_shoulder(7-9)      |  		left_elbow(13-15)       | 		x0y
         % P3	|	right_shoulder(10-12)	|  		right_elbow(16-18)      | 		y0z 
         % P4	|	right_shoulder(10-12)	|  		right_elbow(16-18)      |       x0y
         i1=2; P1=[parts{1,3*i1+1},parts{1,3*i1+2},parts{1,3*i1+3}];
         i2=4; P2=[parts{1,3*i2+1},parts{1,3*i2+2},parts{1,3*i2+3}];
         angleInDegrees3=Line_to_Plane_Angle(P1,P2,1);
         angleInDegrees4=Line_to_Plane_Angle(P1,P2,2); clear P1 P2;
         
         i1=3; P1=[parts{1,3*i1+1},parts{1,3*i1+2},parts{1,3*i1+3}];
         i2=5; P2=[parts{1,3*i2+1},parts{1,3*i2+2},parts{1,3*i2+3}];
         angleInDegrees5=Line_to_Plane_Angle(P1,P2,1); 
         angleInDegrees6=Line_to_Plane_Angle(P1,P2,2); clear P1 P2;
         
         % C.	Distance between two joints-lines
         % d1= line_segment[left_shoulder(7-9)-left_elbow(13-15)]-line_segment[right_shoulder(10-12)-right_elbow(16-18)]
         %  using script  distBW2lines
         x0=[parts{1,7},parts{1,8},parts{1,9}];y0=[parts{1,13},parts{1,14},parts{1,15}];% [left_shoulder-left_elbow] line
         L1 = [x0;y0];      % see lines 85-86 above for explanations
         u=[parts{1,10},parts{1,11},parts{1,12}];v=[parts{1,16},parts{1,17},parts{1,18}];
         L2 =  [u;v];           %  [right_shoulder-right_elbow] line
         d = distBW2lines(L1,L2); clear x0 y0 u v L1 L2;  % d is the minimum distance between L1 and L2
               
         % P.S: D. 	Lower-limbs characteristic trees <--> not tackled just yet
         
         % Assemble in one array the whole v-parameters cell
          v{1,1}=angl1; v{1,2}=angl2; v{1,3}=angl3; v{1,4}=angl4; v{1,5}=angl5;        
          v{1,6}=angl6; v{1,7}=angl7; v{1,8}=angl8 ; v{1,9}=angl9; v{1,10}=angl10;        
          v{1,11}=angl11; v{1,12}=angl12; v{1,13}=angl13; v{1,14}=angl14; v{1,15}=angl15;
          v{1,16}=angleInDegrees1; v{1,17}=angleInDegrees2; v{1,18}=angleInDegrees3;
          v{1,16}=angleInDegrees4; v{1,17}=angleInDegrees5; v{1,18}=angleInDegrees6;
          v{1,19}=d;
      end
      elseif (mod((Ncoord+1),3)~= 0),
                  disp('Wrong No. of coordinates!');
          return;
      end
      % We can also display all data-file in one "large sausage":  
     while ischar(tline)
              disp(tline);    
              tline = fgetl(fileID);  
     end


 fclose(fileID);
