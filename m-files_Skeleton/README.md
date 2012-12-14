csvimport 	= reads from csv text files

read_skel 	= displays 2D skeleton from Kinect SDK

DrawSkeleton 	= displays 3D data from 15 joints see link: http://pr.cs.cornell.edu/humanactivities/data.php

For "filtering-out" bad examples (for training / testing purposes) a  filtering script (filter_export) was used:

https://github.com/ami-lab/AmI-Platform/blob/master/filter_export.py
 
 this one uses a "master-file" which gives the indexes of good skeletons (obtained after a visual inspection) or after a "pre-filtering" based 
 
 on skeleton-resemblance (entropy) with the following syntax:
  
python filter_export.py -f filters.txt -i CSV -o CSV-filtrate
  
where:
  
filters.txt (it's the  "master file" of indexes to be retained)
  
CSV is the origin folder (where all the .csv skeleton files are kept before filtering) 
  
CSV-filtrate is the destination folder (where all the .csv skeleton files that are kept after filtering are to be written) 

PS: this latter folder (CSV-filtrate) is created automatically by filter_export.py if doesn't exist a-priori)
 
