function angle=Kinect_Features_Compute(varargin)
% Function that gives the angle between 3 3D points 
% It relies on a previously written script Features_Compute which returns
% the angle of a triplet of 3D points
% i1, i2 and i3 are the indexes in 'part' the cell-array that contains all the 45 
% coordinates of the joints corresponding to the human skeleton from Kinect
% Shuld get like 4 params (from the workspace):parts, i1, i2 & i3
[~,n]=size(varargin);
if (n<3)
    disp('The function takes at least three input arguments')
    return;
elseif (n >4)
    disp('The funtion takes no more than four input arguments.')
    return;
elseif n == 4
    disp('4 inputs given')
     parts= varargin{1}; i1=varargin{2}; i2=varargin{3}; i3=varargin{4}; %#ok<*NASGU>
elseif n == 3
    disp('3 inputs given')
    % By default, if there are 3 params i1 is considered 0; i.e. 1st point is the Head of the subject
    parts= varargin{1}; i1=0; i2=varargin{2}; i3=varargin{3};
end

parts= varargin{1}; 
i1=varargin{2}; % i is the index of the body part; i = 0...14; i ==0 (Head), i=1 (Neck)... i=14 (right_foot)
         x1=[parts{1,3*i1+1},parts{1,3*i1+2},parts{1,3*i1+3}];
         
i2=varargin{3}; x2=[parts{1,3*i2+1},parts{1,3*i2+2},parts{1,3*i2+3}];

i3=varargin{4}; x3=[parts{1,3*i3+1},parts{1,3*i3+2},parts{1,3*i3+3}]; clear i; pause(0.01);

angle= Features_Compute(x1,x2,x3);