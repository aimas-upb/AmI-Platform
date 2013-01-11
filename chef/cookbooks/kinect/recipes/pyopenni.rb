package "cmake" do
    action :install
end

package "build-essential" do
	action :install
end

package "git-core" do
	action :install
end

package "python-dev" do
	action :install
end

package "libboost-python-dev" do
	action :install
end

directory "PyOpenDir" do
    action :create
    path "#{node.pyopen.path}/PyOpenNI"
    user node.user_name
end

git "pyopen" do
    repository "git://github.com/jmendeth/PyOpenNI.git"
    revision "HEAD"
    user    node.user_name
    destination "#{node.pyopen.path}/PyOpenNI"
    action :sync
end

directory "PyOpenBuild" do
    action :create
    path "#{node.pyopen.path}/PyOpen-build"
end

script "compile" do
    interpreter "bash"
    cwd "#{node.pyopen.path}/PyOpen-build"
    code <<-EOH
    cmake ../PyOpenNI
    EOH
end
