function Create_Bounds_Intervals( varargin )
%CREATE_BOUNDS_INTERVALS This function helps establishing the upper and
% lower bounds for the variables used in posture_assessment toolbox
% It writes in a folder called 'intervals' the values of all the 22
% variables recorded in the current experiment (is helping parametrization)
% 
% See also: CellArray_to_Csv.m function
%   The inputs are as it follows:
%     - train_labels.csv (gives the labels of all the experiments -all the postures-instances collections
%     -           
cd '/home/JohnDoe/';
RESULT = csvimport('train_labels.csv');
 m=size(RESULT,1);
  
 for iv = 1:m, % grab one collection at-a-time
     cd '/home/JohnDoe/data/filtered-CSV/';
    InstanceName1 = RESULT{iv,1}; InstanceName= strtrim(InstanceName1); clear InstanceName1 fid; 
    
    pause(0.01);
    data= getAllRecordParams(InstanceName);
    
    clear fid; fid = fopen(InstanceName,'w');
    cd 'E:\intervals\'; % go to the folder of the new repository
    for iii=1:length(data)-1,
        maxNRows = max([length(data{iii}) length(data{iii+1})]);
    end
    for ii=1:maxNRows,      %% 1 -> 22 rows (No of variables)
    for i=1:length(data),   %% 1 -> No_of_Records columns
        try 
            if iscell(data{i}),
                fprintf(fid,'%s,',cell2mat(data{i}(ii)));
            else
                fprintf(fid,'%f,',data{i}(ii));
            end
        catch ME %#ok<NASGU>
            fprintf(fid,',');
        end
    end
    fprintf(fid,'\n');
    end
    fclose(fid);
    disp('Finished a Record-collection; press a key'); clear ii iii;
    iv= iv+1;
    pause
 end
end

