#
# Cookbook Name: :ami-node
# Recipe: :default
#
# Copyright 2012, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#


include_recipe "ami-node::default_libs"
include_recipe "ami-node::default_tools"
include_recipe "ami-node::user_ami"
include_recipe "openVPN::default"
include_recipe "nagios::default"

