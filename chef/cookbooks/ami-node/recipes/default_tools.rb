#
# Cookbook Name: :ami-node
# Recipe: :default
#
# Copyright 2012, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#
package "tar" do
	action :install
end

package "zip" do
    action :install
end

package "git" do
    action :install
end

package "python" do
	action :install
end

package "python-dev" do
	action :install
end

package "python-pip" do
	action :install
end

package "python-opencv" do
	action :install
end

package "monit" do
    action :install
end
