function OUT = find_posture( varargin )
%The FIND_POSTURE - This function returns here the body-posture of a subject 
%   resulted after the evaluation of the parameters of a skeleton from Kinect:
%    http://www.microsoft.com/en-us/kinectforwindows/
%  INPUTS:  - first param is the training set
%           - second param is the skeleton dataset currently examined
% See also: getAllRecordParams
OUT = []; % Initialize
% Start checking input params
[~,n]=size(varargin);
if (n~=2),
    disp('Wrong number of input arguments, it should be equal to 2!')
    return;
elseif (n == 2),
    disp('2 inputs given')
    disp('The 1st argument gives the train file name,ie the CSV of all the recorded body-postures')
    a =  varargin{1};  %#ok<*NASGU>
    b =  varargin{2}; 
end
% Use EXIST function which returns:
%         0 if A does not exist
%         1 if A is a variable in the workspace
%         2 if A is an M-file on MATLAB's search path. It also returns 2 when
%            A is the full pathname to a file or when A is the name of an
%            ordinary file on MATLAB's search path
%         3 if A is a MEX-file on MATLAB's search path
if exist('csvimport.m','file')==2,
    disp('Add script csvimport.m to your path first...')
    disp('This is a link to <a href="http://www.mathworks.com/matlabcentral/fileexchange/23573-csvimport/content/csvimport.m">csvimport</a>.')
    return
end
pause(0.001);
if exist('createLine3d.m','file')==2,
   disp('This function relies on some scripts from the MatGeom Project:')
   disp('This is a link to <a href="http://sourceforge.net/apps/mediawiki/matgeom/index.php?title=Main_Page">MatGeom</a>.')
    return
end
pause(0.001);

variables = {'head_x','head_y', 'head_z', 'neck_x','neck_y','neck_z',... 
    'left_shoulder_x', 'left_shoulder_y','left_shoulder_z',...
    'right_shoulder_x','right_shoulder_y','right_shoulder_z',...
 	  'left_elbow_x','left_elbow_y','left_elbow_z', ... 
      'right_elbow_x','right_elbow_y','right_elbow_z',... 
      'left_hand_x','left_hand_y','left_hand_z', ...
      'right_hand_x','right_hand_y', 'right_hand_z' ...
 	  'torso_x','torso_y','torso_z', 'left_hip_x','left_hip_y','left_hip_z',... 
      'right_hip_x','right_hip_y','right_hip_z','left_knee_x','left_knee_y','left_knee_z',...
      'right_knee_x','right_knee_y','right_knee_z',...
      'left_foot_x','left_foot_y','left_foot_z',...
      'right_foot_x','right_foot_y','right_foot_z'};
N = length(variables);
% create variables for indexing
for v = 1:N,
    eval([variables{v},' = ', num2str(v),';']);
end
lb = zeros(size(variables)); % The lower-bounds for Optim. Tbox


ub = Inf(size(variables));  % The upper-bounds for Optim. Tbox


end

