function ALL_FILE = build_all_train(varargin) 
% The BUILD_ALL_TRAIN function takes all the names of the record from the
% "labels-file" named 'train_labels.csv' and builds a file for train
% purposes from which testing instances will be selected as well:
%
cd '/home/JohnDoe/data/filtered_CSV/';
RESULT = csvimport('train_labels.csv');
ALL_FILE= [];
 m=size(RESULT,1);
% The stored variables, mainly angles (see getParameters.m) are stored in
% ALL_FILE array like in a LIFO-stack (ie first angles from the 1st recorded 
% instance of 1st position, ie "stand_jos" remain at the very BOTTOM of 'ALL_FILE'
 for i = 1:m,
    filename1 = RESULT{i,1}; filename= strtrim(filename1); clear filename1;
    OUT = getAllRecordParams(filename);  %clear filename;
    ALL_FILE= cat(1,OUT,ALL_FILE);  pause(0.001); %clear OUT;
    i=i+1;     %#ok<FXSET>
 end
