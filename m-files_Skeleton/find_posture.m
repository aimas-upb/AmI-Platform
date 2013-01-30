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
if exist('csvimport.m','file')==2, % After I create MEX should check for ==3
    disp('Add script csvimport.m to your path first...')
    disp('This is a link to <a href="http://www.mathworks.com/matlabcentral/fileexchange/23573-csvimport/content/csvimport.m">csvimport</a>.')
    return
end
pause(0.001);
if exist('createLine3d.m','file')==2, % After I create MEX should check for ==3
   disp('This function relies on some scripts from the MatGeom Project:')
   disp('This is a link to <a href="http://sourceforge.net/apps/mediawiki/matgeom/index.php?title=Main_Page">MatGeom</a>.')
    return
end
pause(0.001);
% T1 	|   	head(1-3)               |  		neck(4-6)               |   left_shoulder(7-9)      | HNL_S = angl1 
% T2 	|   	head(1-3)               |  		neck(4-6)               |   right_shoulder(10-12)   | HNR_S = angl2 aso
% T3 	|  	neck(4-6)               |  		left_shoulder(7-9)      |   left_elbow(13-15)       | NL_SL_E  ...
% T4 	|  	neck(4-6)               |  		right_shoulder(10-12)	|   right_elbow(16-18)      | NR_SR_E ...
% T5	|  	left_shoulder(7-9)      | 		left_elbow(13-15) 	|   left_hand(19-21)        | L_SL_EL_H
% T6	|  	right_shoulder(10-12)	| 		right_elbow(16-18)      |   right_hand(22-24)       | R_SR_ER_H
% T7	|	head(1-3)               |  		neck(4-6)               |   torso(25-27)            | HNT
% T8	|	neck(4-6)               |  		torso(25-27)            |   left_hiP(28-30)         | NTL_P
% T9	|	neck(4-6)               |  		torso(25-27)            |   right_hiP(31-33)        | NTR_P
% T10	| 	torso(25-27)            | 		left_hiP(28-30)         |   left_Knee(34-36)        | TL_PL_K
% T11	| 	torso(25-27)            | 		right_hiP(31-33)        |   right_Knee(37-39)       | TR_PR_K
% T12	| 	left_hiP(28-30)         |		left_Knee(34-36)        |   left_foot(40-42)        | L_PL_KL_F
% T13	| 	right_hip(31-33)        |		right_knee(37-39)       |   right_foot(43-45)       | R_PR_KR_F
% T14	|	neck(4-6)               |  		torso(25-27)            |   left_Knee(34-36)        | NTL_K
% T15	|	neck(4-6)               |  		torso(25-27)            |   right_Knee(37-39)       | NTR_K =angl15
% See getParameters.m for the signficance of the rest of 7 variables
variables = {'angl1', 'angl2','angl3',... 
            'angl4','angl5','angl6',...
            'angl7','angl8','angl9',...
            'angl10','angl11','angl12',... 
            'angl13','angl14','angl15',...
            'aID1','aID2','aID3','aID4','aID5','aID6','d'};
N = length(variables);
% create variables for indexing
for v = 1:N,
    eval([variables{v},' = ', num2str(v),';']);
end
lb = zeros(size(variables)); % The lower-bounds for Optim. Tbox


ub = Inf(size(variables));  % The upper-bounds for Optim. Tbox


end

