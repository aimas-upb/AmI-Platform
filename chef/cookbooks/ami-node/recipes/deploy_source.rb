git "ami-repo" do
    destination "/home/#{node.user_name}/#{node.ami_platform.path}"
    repository  "git://github.com/ami-lab/AmI-Platform.git"
    revision "master"
    user node.user_name
    action :sync
end

#Install python requirements before executing and after deploying source.
include_recipe "ami-node::python_requirements"

script "execute" do
    interpreter "bash"
    cwd "/home/#{node.user_name}/#{node.ami_platform.path}"
    code <<-EOH
	./deploy.sh
    EOH
end
