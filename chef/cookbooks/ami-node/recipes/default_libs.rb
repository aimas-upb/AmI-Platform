#
# Cookbook Name: :ami-node
# Recipe: :default
#
# Copyright 2012, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#
package "libshadow-ruby1.8" do
    action :install
end

package " libmemcached-dev" do
	action :install
end