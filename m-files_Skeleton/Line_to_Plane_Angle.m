function angleInDegrees=Line_to_Plane_Angle(varargin) 
% Returns the angle between a line (given by two points)
% and a plane, (which can be given by it's equation)
% varargin should provide at most 3 arguments:
%               - 3D coordinates of the 1st and 2nd point
%               - equation of the plane or the TYPE of the plane, which is: 
%                   '1' for yOz,'2' for 'xOy' 
%  it relies on the MatGeom Project:
% http://sourceforge.net/apps/mediawiki/matgeom/index.php?title=Main_Page
% See also : MRI Kinematics Reconstruction Toolkit
% http://code.google.com/p/mkrtk/source/detail?r=f6aeef8eb73c96b19595e835dddd86c29ca91966
%                   ^Y
%                   |
%                   |
%                   |
%                   |
%                   ------------------>X
%                  /
%                 /
%                /
%               Z
 
%% 1st let's fit a 3D line between the 2 points ..
P1 = varargin{1};
P2 = varargin{2};
L = createLine3d(P1, P2); 

%% The Plane considered in our case (skeletons from Kinect) is either 'yOz' or 'xOy'
% for type 1 (yOz):
x1=P1(1,1); y1=0; z1=0; p1=[x1, y1, z1]; % on the 'X'-axis (abscissa)
x2=x1; y2=0; z2=P1(1,3); p2=[x2, y2, z2]; % definitely on the xOz plane
% Now, create a plane from the 3 points:
plane = createPlane(P1, p1, p2);

% To check, compute intersection of the line with the above plane:
% Should be definitely P1, otherwise an error has occured:
inter = intersectLinePlane(L, plane);
if max(P1-inter)>(10^4)*eps,    
    disp('Error! ')
else return
end
%%  parametrize the  plane and the line:
% The plane is given by:
x=P1(1,1);      %#ok<*NASGU> % or 
% The line is parametrized as being parallel to the vector v=P1?P2 ==>
syms t
X = P1 + t*(P1-P2); %  if we write X= (x,y,z) ==>
x=X(1);
y=X(2);
z=X(3);

% By a series of 2 consecutive translations of the line, we get the formulas:
l1 = sqrt((P2(1,1)-P1(1,1))^2+(P2(1,3)-P1(1,3))^2);
theta=atan(l1/abs(P1(1,2)-P2(1,2))); 
angleInDegrees = radtodeg(theta) %#ok<NOPRT>

