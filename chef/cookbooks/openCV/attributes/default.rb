#Defaults for OpenCV installation.
default["openCV"]["version"] = "2.4.3"
default["openCV"]["directoryName"] = "OpenCV-#{node.openCV.version}"
default["openCV"]["archive"] = "#{node.openCV.directoryName}.tar.bz2"
default["openCV"]["sourceURL"] = "http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.4.3/#{node.openCV.archive}/download"
default["openCV"]["destination"]["source"] = "/home/#{node.user_name}/OpenCV"
default["openCV"]["destination"]["archives"] = "#{node.openCV.destination.source}/downloads"
default["openCV"]["installationDirectory"] = "/usr/local"