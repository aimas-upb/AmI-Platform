#
# Cookbook Name: :ami-daq
# Recipe: :default
#
# Copyright 2012, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

include_recipe "ami-node::default"
include_recipe "ami-daq::monit"
include_recipe "ami-daq::deploy_source"
