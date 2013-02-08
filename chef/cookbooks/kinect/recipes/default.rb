#
# Cookbook Name: :kinect
# Recipe: :default
#
# Copyright 2012, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#


include_recipe "kinect::supp_libs"
include_recipe "kinect::source_directory"
include_recipe "kinect::openni_drivers"
include_recipe "kinect::avin2_drivers"
include_recipe "kinect::nite_drivers"
include_recipe "kinect::pyopenni"
