#
# Cookbook Name: :ami-node
# Recipe: :default
#
# Copyright 2012, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

include_recipe "ami-node::user_ami"
include_recipe "ami-node::git"
include_recipe "ami-node::tar"
include_recipe "ami-node::zip"
include_recipe "python::default"

