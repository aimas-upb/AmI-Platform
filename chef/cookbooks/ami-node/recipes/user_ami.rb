package "libshadow-ruby1.8" do
    action :install
end

group "group" do
	group_name node.user_group
	action :create
end

user "user" do
    action :create
    username node.user_name
    gid 	node.user_group
    home    "/home/#{node.user_name}"
    shell "/bin/bash"
    password node.password_hash
    supports :manage_home => true
end

script "chg_hostname" do
	interpreter "bash"
	code <<-EOH
	sudo hostname #{node.user_name}-#{node.node_type}-#{node.node_index}
	EOH
end
