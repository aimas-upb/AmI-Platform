#
# Cookbook Name: :ami-crunch
# Recipe: :default
#
# Copyright 2013, AmI-Lab
#
# All rights reserved - Do Not Redistribute
#

include_recipe "ami-node::default"
include_recipe "ami-node::monit"
include_recipe "openCV::default"
include_recipe "ami-node::deploy_source"
