git "ami-repo" do
    destination "/home/#{node.user_name}/#{node.ami_platform.path}"
    repository  "git://github.com/ami-lab/AmI-Platform.git"
    revision "master"
    user node.user_name
    action :sync
end

#Install python requirements before executing and after deploying source.
include_recipe "ami-node::python_requirements"

#Export server variables
#template "/etc/profile.d/local.sh" do
#    source "local.sh.erb"
#    mode 0640
#    owner "root"
#    group "root"
#    variables ({
#        :kestrel_server => node[:kestrel_server],
#        :kestrel_port => node[:kestrel_port]
#        })
#end

script "env_vars" do
    interpreter "bash"
    cwd "/etc"
    code <<-EOH
	echo  "AMI_KESTREL_SERVER_IP=#{node.kestrel_server}" | sudo tee -a environment
	echo  "AMI_KESTREL_SERVER_PORT=#{node.kestrel_port}" | sudo tee -a environment
    EOH
end


template "settings.py" do
    source "settings.py.erb"
    owner node.user_name
    group node.user_group
    path  "/home/#{node.user_name}/#{node.ami_platform.path}/core/settings.py"
    variables ({
        :kestrel_server => node[:kestrel_server],
        :kestrel_port => node[:kestrel_port],
        :mongodb_server => node[:mongodb_server],
        :mongodb_port => node[:mongodb_port]
    })
end

template "services.txt" do
    source "services.erb"
    owner node.user_name
    group node.user_group
    path  "/home/#{node.user_name}/#{node.ami_platform.path}/services.#{node.user_name}-#{node.node_type}-#{node.node_index}.txt"
    variables ({
        :services => node[:services]
    })
end

script "execute" do
    interpreter "bash"
    cwd "/home/#{node.user_name}/#{node.ami_platform.path}"
    code <<-EOH
	./deploy.sh
    EOH
end
