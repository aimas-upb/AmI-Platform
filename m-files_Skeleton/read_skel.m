addpath 'D:\Docs\ERRIC\Manifolds\';
addpath 'D:\Docs\ERRIC\Date\';
[cc, i, cc, xr, yr, zr, cc, x, y] = textread('res1.txt', '%c %d %c %f %f %f %c %d %d');
[m n] = size(x);
no_skeletal = m/20;
A=[];  %A = {}; % This cell-aray will contain the (xr,yr,zr)
xlim([5 300]); ylim([5 500])
plot([5, 300], [0, 0]);
hold on;
plot([0, 0], [0, 500]);
hold on;
grid on;
i=1;
j=0;
y = 500-y;
set(gca, 'YTickLabel', num2str(get(gca, 'YTick')));

while i <= no_skeletal
    title(['Image is for frame Number: ', num2str(i)])
    plot([x(4+j),x(3+j)],[y(4+j),y(3+j)])
    hold on;
    plot([x(5+j),x(3+j)],[y(5+j),y(3+j)])
    hold on;
    plot([x(9+j),x(3+j)],[y(9+j),y(3+j)])
    hold on;
    plot([x(2+j),x(3+j)],[y(2+j),y(3+j)])
    hold on;
    plot([x(2+j),x(1+j)],[y(2+j),y(1+j)])
    
    hold on;
    plot([x(5+j),x(6+j)],[y(5+j),y(6+j)])
    hold on;
    plot([x(7+j),x(6+j)],[y(7+j),y(6+j)])
    hold on;
    plot([x(7+j),x(8+j)],[y(7+j),y(8+j)])
    hold on;
    plot([x(9+j),x(10+j)],[y(9+j),y(10+j)])
    hold on;
    plot([x(10+j),x(11+j)],[y(10+j),y(11+j)])
    hold on;
    plot([x(11+j),x(12+j)],[y(11+j),y(12+j)])
    hold on;
    plot([x(13+j),x(1+j)],[y(13+j),y(1+j)])
    hold on;
    plot([x(17+j),x(1+j)],[y(17+j),y(1+j)])

    hold on;
    plot([x(13+j),x(14+j)],[y(13+j),y(14+j)])
    hold on;
    plot([x(17+j),x(18+j)],[y(17+j),y(18+j)])
    
    hold on;
    plot([x(15+j),x(14+j)],[y(15+j),y(14+j)])
    hold on;
    plot([x(19+j),x(18+j)],[y(19+j),y(18+j)])
    
    hold on;
    plot([x(15+j),x(16+j)],[y(15+j),y(16+j)])
    hold on;
    plot([x(19+j),x(20+j)],[y(19+j),y(20+j)])
    
    X=xr((i-1)*20+1:(i-1)*20+20);
    Y=yr((i-1)*20+1:(i-1)*20+20);
    Z=zr((i-1)*20+1:(i-1)*20+20);
    A{i}=[X,Y,Z]; clear X Y;
    % Compute X_c and Y_c the coordinates of the figure's center:
    pause
     clf reset %clear figure's props
    %clc% Is doing figures super-imposing 
    i=i+1;
    j=j+20;
end
if exist('A1.mat')==0, %#ok<EXIST>
    save A1 A
end
%%-------------------------------------------------
% Load all the .mat matrices and create the "patch"
% First, list 'em all in a file:
!ls -1 *.mat > list.txt
disp('Read the list of records now... for that, press a key')
pause
file = textread('list.txt','%s','delimiter','\n','whitespace','');
m=size(file,1);
% now, load the all ...
for j =1 : m,
   % ss = strcat(’cos(’,num2str(n),’x)’);
    ss = horzcat('load','  ','A',num2str(j),'.mat')';
    eval(ss);
    pause
    ss1 = horzcat('A',num2str(j),'=','A');
    eval(ss1);
    clear ss ss1;
    
end
A= []; % the container initialized for the patch
clear j;

%% gotta translate cell-arrays in matrices; initialize with A1: 
C1= []; % C1 will contain the cell-->2 matrix result of A1
n=size(A1,2); C1=A1{1,1};  %#ok<USENS>
for j = 2:n,
    tt=A1{1,j};
    C1=cat(1,C1,tt); 
    clear tt ;
end

save C1 C1; 
clear n j;
% and, now, similar with all the other 'm-1' cell-arrays, prev. saved on HDD
for i = 2:m,
    % Ci = celula2mat(Ai);
    ss = horzcat('C',num2str(i),'=','celula2mat','(','A',num2str(i),');');
    eval(ss); disp('Press a key')
    pause
    clear ss; % Now:  tt=Aj{1,i};Ci=cat(1,Ci,tt); clear tt;
    
end
clear i;
%% Now, I concatenate them in one large slim-matrx 'C'
C = [];
C=cat(2,C,C1);
for i=2:m,
    % like: C = cat(1, C, C3); recursively
    ss = horzcat('C','=','cat(1',',','C',',','C',num2str(i),')',';')' %#ok<NOPTS>
    eval(ss);
    clear ss;
    disp(i)
     disp('Press a key')
    pause
end
%% Now create the  "patch" (one large matrx with 60-elem vectors /line'
split = 60; % 60 /3 (ie : X, Y, Z for each line)
clear A A1 A2 A3 A4 A5 A6 A7 A8;
clear A9 A10 A11 A12 A13 A14;
no_skelets4_test =(size(C,1))/20; 
CC=C';  % cause I take them 'row-by-row'
B=CC(:);
patch = zeros(no_skelets4_test,split);

patch(1,:)=B(1:split);
for i=2:no_skelets4_test,
    patch(i,:)=B((i-1)*split+1:(i*split));
    disp(i)
     disp('Press a key')
    pause
end
