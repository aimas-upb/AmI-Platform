function v = getParams(varargin) 
% Function to compute all features from a line of the CSV (from Kinect skeleton);
% These features are to be used by a classifier to assess the body-posture
%  The 4 types of params (features) computed from each line are:
% 1) the angle between any triplet (of interest) of 3D points given by Kinect_Features_Compute(i1,i2,i3)
% 2) the angle of the line (formed by 2 pairs of 3D points) with y0z plane
% both 2) & 3) given by Line_to_Plane_Angle
% 3) the angle of the line (formed by 2 pairs of 3D points) with x0y plane
% 4) the distances between pairs of body-segments  (i.e. vectors)using dist2lines

[~,n]=size(varargin);
if (n~=1),
    disp('Wrong number of input arguments!')
    return;
elseif (n == 1),
    disp('The function takes  one input argument-the file name')
    a=  varargin{1};
end
cd E:\new_CSV\CSV-filtrate\; % cd /home/JohnDoe/data/filtered_CSV/;
% The folder where the repository of filtered-CSVs is to be found

 % Name of the files in that folder are Like: filename = 'export-AD_dreapta_sus.csv'; 
% listing = dir('*.csv');
% m = size(listing,1); % The Number of filtered records in the analysed folder

 clear fileID;   idx= 0;
 fileID = fopen(a); %#ok<*NASGU>
     % Get the 1st line of coordinates:
     tline = fgetl(fileID);
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
         i=0; % i is the index of the body part; i = 0...14; i ==0 (Head), i=1 (Neck)... i=14 (right_foot)
         x1=[parts{1,3*i+1},parts{1,3*i+2},parts{1,3*i+3}];
         i=1; x2=[parts{1,3*i+1},parts{1,3*i+2},parts{1,3*i+3}];
         i=2; x2=[parts{1,3*i+1},parts{1,3*i+2},parts{1,3*i+3}]; clear i; pause(0.01);
         angl1= Features_Compute(x1,x2,x3);
         
         % 	  II. Compute angles from Pairs_of_Points to Planes /distance (using Line_to_Plane_Angle):
         % A. body trunk characteristic tree (MSc-Thesis Diana Tatu, Chpter 3-Architecture.docx)
         % P1	|	neck(4-6)               |  		torso(25-27)            | 		y0z
         % P2	|	neck(4-6)               |  		torso(25-27)            | 		x0y
         %
         % B. 	Upper-limbs characteristic trees (using Line_to_Plane_Angle):
         % P1	|	left_shoulder(7-9)      |  		left_elbow(13-15)       | 		y0z
         % P2	|	left_shoulder(7-9)      |  		left_elbow(13-15)       | 		x0y
         % P3	|	right_shoulder(10-12)	|  		right_elbow(16-18)      | 		y0z 
         % P4	|	right_shoulder(10-12)	|  		right_elbow(16-18)      |       x0y
        
         
         % C.	Distance between joints-line and joints-line
         % d1= line_segment[left_shoulder(7-9)-left_elbow(13-15)]-line_segment[right_shoulder(10-12)-right_elbow(16-18)]
         %  using script  distBW2lines
         %          
         % D. 	Lower-limbs characteristic trees <--> not tackled just yet
         
         x0=[parts{1,7},parts{1,8},parts{1,9}];y0=[parts{1,13},parts{1,14},parts{1,15}];% [left_shoulder-left_elbow] line
         L1 = [x0;y0];      % see lines 85-86 above for explanations
         u=[parts{1,10},parts{1,11},parts{1,12}];v=[parts{1,16},parts{1,17},parts{1,18}];
         L2 =  [u;v];           %  [right_shoulder-right_elbow] line
         d = distBW2lines(L1,L2); clear x0 y0 u v L1 L2;  % d is the minimum distance between L1 and L2
         
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
