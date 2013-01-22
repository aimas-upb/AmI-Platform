function OUT = getAllRecordParams(varargin)  %#ok<*STOUT>
% Function to compute all features from all lines of a CSV (from Kinect skeleton);
%
% These features are to be used by a classifier to assess the body-posture
%  The 4 types of params (features) computed from each line are:
% 1) the angle between any triplet (of interest) of 3D points given by Kinect_Features_Compute(i1,i2,i3)
% 2) the angle of the line (formed by 2 pairs of 3D points) with y0z plane
% both 2) & 3) given by Line_to_Plane_Angle
% 3) the angle of the line (formed by 2 pairs of 3D points) with x0y plane
% 4) the distances between pairs of body-segments  (i.e. vectors) using distBW2lines
% 
%  Needs one input parameters:  the name of the file (e.g.'export-AD_dreapta_sus.csv')
% See also: getParams, which returns the cell-array of params only for one
% instance (frame from the Kinect)
 cd /home/JohnDoe/data/filtered_CSV/;

[~,n]=size(varargin);
if (n~=1),
    disp('Wrong number of input arguments, it should be equal to 1!')
    return;
elseif (n == 1),
    disp('1 inputs given')
    disp('The  argument gives the file name,ie the CSV of the recorded body-posture')
    a=  varargin{1}; %#ok<*NASGU>
end
 % like  a=listing(1,1).name     %#ok<NOPRT> % The record's name
  fid = fopen(a,'r');
C = textscan(fid, '%s','delimiter', '\n'); % Read the whole file in a cell-array
l=1;
  if fid > 0,
      C1= C{1,1};
      m = size(C1,1);  % The no. of instances of the same posture in a CSV-record is given by 'm'
      OUT = cell(m,1); % Initialize the Output-cell-array with a blank one
      l=1; v= getParams(a,l); pause(0.01); OUT{1,1}=v; clear v;
    
   while le(l,m-1),   % get each instance, 'one-by-one'
          l=l+1;  
          v= getParams(a,l);
          % Record each results vector 'v' & save it
          pause(0.01);
          OUT{l,1}=v; clear v;
   end
  elseif fid == 0,
      disp('Error in reading CSV-file, try again');
  end
  
