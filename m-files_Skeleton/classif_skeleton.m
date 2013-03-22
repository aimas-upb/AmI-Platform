cd /home/amilab/Dropbox/DateSkeleton;
data = load('ShuffledTrainData.dat');
X = data(:,1:20);
y = data(:,21);
dat.X = X';
dat.y = y'; clear data;

c = cvpartition(y,'k',10);
fun = @(xT,yT,xt,yt)(sum((yt - classify(xt,xT,yT)) == 0,1));


%%
test = crossval(fun,X,y,'partition',c)
%rate = sum(crossval(fun,X,y,'partition',c)) * 100 /sum(c.TestSize)
%res = sum(~strcmp(yt,classify(xt,xT,yT)))%/size(xt,1)
%test = yt - classify(xt,xT,yT);
%sum(test == 0,1) * 100 / size(xt,1)