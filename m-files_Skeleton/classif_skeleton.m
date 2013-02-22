cd /home/JohnDoe/Data/;
data = load('ShuffledTrainData.dat'); %data=load('train1.dat');
X = data(:,1:20);
y = data(:,21);
dat.X = X'; 

dat.y = y'; clear data;
c = cvpartition(y,'k',10);

fun = @(xT,yT,xt,yt)(sum(~strcmp(yt,classify(xt,xT,yT))));

rate = sum(crossval(fun,X,y,'partition',c))/sum(c.TestSize)
