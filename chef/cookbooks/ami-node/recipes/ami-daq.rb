#
# Cookbook Name: :ami-daq
# Recipe: :default
#
# Copyright 2012, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

include_recipe "ami-node::default"
include_recipe "kinect::default"
include_recipe "ami-node::deploy_source"
