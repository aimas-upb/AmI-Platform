git "ami-repo" do
    destination "/home/#{node.user_name}/#{ami-platform.path}"
    repository  "git://github.com/ami-lab/AmI-Platform.git"
    revision "master"
    user node.user_name
    action :sync
end

script "execute" do
    interpreter "bash"
    cwd "/home/#{node.user_name}/#{ami-platform.path}"
    code <<-EOH
 	./deploy.sh
    EOH
end
