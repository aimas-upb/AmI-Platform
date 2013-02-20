#
# Cookbook Name: :nagios
# Recipe: :default
#
# Copyright 2012, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#
package "nagios-nrpe-server" do
	action :install
end

remote_file "nagios-cfg" do
	action :create
	path "/etc/nagios/nrpe.cfg"
	owner "root"
	source node.nagios.nrpe_cfg
end


remote_file "cmd-cfg" do
	action :create
	path "/etc/nagios/nrpe_local.cfg"
	owner "root"
	source node.nagios.commands_cfg
end

service "nagios-nrpe-server" do
	action :reload
end