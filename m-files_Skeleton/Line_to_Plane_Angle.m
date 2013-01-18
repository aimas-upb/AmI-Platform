function angleInDegrees=Line_to_Plane_Angle(varargin) 
% Returns the angle between a line (given by two points)
% and a plane, (which can eventually be given by it's equation)
% varargin should provide at most 3 arguments:
%               - 3D coordinates of the 1st and 2nd point
%               - equation of the plane or the TYPE of the plane, which is: 
%                   '1' for yOz,'2' for 'xOy' 
%  it relies on some scripts from the MatGeom Project:
% http://sourceforge.net/apps/mediawiki/matgeom/index.php?title=Main_Page
[~,n]=size(varargin);
if (n<2)
    disp('The function takes at least two input arguments')
    % By default, if there are 2 params the plane is considered yOz
    return;
elseif (n >3)
    disp('The funtion takes no more than three input arguments.')
    return;
elseif n == 2
    disp('2 inputs given')
    disp('the plane is considered yOz by default')
    type = 1;
    x1=varargin{1}(1,1);y1=varargin{1}(1,2);z1=varargin{1}(1,3);P1 = [x1,y1,z1];
    x2=varargin{2}(1,1);y2=varargin{2}(1,2);z2=varargin{2}(1,3);P2 = [x2,y2,z2];
    %P2 = varargin{2};
elseif n == 3
    disp('3 inputs given')
    x1=varargin{1}(1,1);y1=varargin{1}(1,2);z1=varargin{1}(1,3);P1 = [x1,y1,z1];
    x2=varargin{2}(1,1);y2=varargin{2}(1,2);z2=varargin{2}(1,3);P2 = [x2,y2,z2];
    type = varargin{3};
end
%% 1st let's fit a 3D line between the 2 points ..
L = createLine3d(P1, P2); 

if type == 1,
    %% The Plane considered in our case (from points obtained from skeletons we get from Kinect)
    %  is either 'yOz' or 'xOy' (depending on the 'type'-input: for type=1 (we compute angle with the 'yOz'-plane):
    x1=P1(1,1); y1=0; z1=0; p1=[x1, y1, z1]; % 'p1' is on the 'X'-axis (preserves  only abscissa from P1)
    x2=x1; y2=0; z2=P1(1,3); p2=[x2, y2, z2]; % 'p2' is on definitely on the xOz plane
    % Now, create a plane from the 3 points:
    plane = createPlane(P1, p1, p2); %
    %  'plane' is the plane || (parallel) to y0z that passes thru the points: P1, p2 & p1
    % To verify the above, compute intersection of the line with the above plane:
    % Should be definitely the point P1, otherwise an error has occured:
    inter = intersectLinePlane(L, plane);
    if max(P1-inter)>(10^4)*eps,    
        disp('Error! ')
    end
    clear inter;
    % Now we perform a series of 2 consecutive translations of the line 'L' (from  above)
    % The first translation brings P1 on the y0z plane (i.e. x1 becomes 0)
    % Point P2 is considered linked (like 'with a bar' to P1) and so, P2 is dragged away  with P1
    % the 2nd translation brings P2 down on the x0z plane (so y2 becomes ==0);
    %therefore,  we get the formulas:
    l1 = sqrt((P2(1,1)-P1(1,1))^2+(P2(1,3)-P1(1,3))^2);
    theta=atan(l1/abs(P1(1,2)-P2(1,2))); clear l1;
    angleInDegrees = radtodeg(theta);
elseif type == 2,%The Plane considered in this case is 'xOy'
    % The angle of the line 'L' with the plane 'x0y' shuld not change by
    % the following two consecutive translations...
    % We follow the same procedure, subjecting line 'L' to 2 consecutive translations like it follows:
    % 1) If we drag the line L parallel to itself until P1 point arrives on the x0y plane :
    % 2) Once it got there, we let line L' (parallel to L) 'sink' on the
    % plane x0z, i.e. until point P1' (projection of P1 onto the x0y plane)i.e. arrives on the  x axis (the abscissa); 
    % the formula of the 'original' line 'L' with the x0y follows immediately:
    l1 = sqrt((P2(1,2)-P1(1,2))^2+(P2(1,3)-P1(1,3))^2);
    theta = atan(l1/abs((P2(1,1)-P1(1,1)))); clear l1;
    angleInDegrees = radtodeg(theta);    
elseif (type ~= 1) && (type ~= 2),
    disp('Error! wrong type'); return;
end



