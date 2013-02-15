#
# Cookbook Name: :kinect
# Recipe: :default
#
# Copyright 2012, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#
package "openvpn" do
	action :install
end

directory "keys" do
	action :create
	owner "root"
	path "/etc/openvpn/keys"
end

remote_file "conf_file" do
	action :create
	path "/etc/openvpn/client.conf"
	owner "root"
	source node.openvpn.config_file_url
end
