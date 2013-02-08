script "pip_install" do
    interpreter "bash"
    cwd "/home/#{node.user_name}/#{node.ami_platform.path}"
    code <<-EOH
	pip install -r #{node.python.requirements_file}
    EOH
end
