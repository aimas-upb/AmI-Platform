directory "source" do
    action :create
    mode 0775
    owner node.user_name
    path node.openCV.destination.source
end

directory "archives" do
    action :create
    mode 0775
    owner node.user_name
    path node.openCV.destination.archives
end

remote_file "openCV" do
    action :create
    path "#{node.openCV.destination.archives}/#{node.openCV.archive}"
    mode 0755
    owner  node.user_name
	source node.openCV.sourceURL
end

script "extract" do
    interpreter "bash"
    cwd node.openCV.destination.archives
    code <<-EOH
    tar xvjf #{node.openCV.archive}
    mv #{node.openCV.directoryName} ../#{node.openCV.directoryName}
    EOH
    
script "install" do
    interpreter "bash"
    cwd "#{node.openCV.destination.source}/#{node.openCV.directoryName}"
    code <<-EOH
    mkdir release
    cd release
    cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX= #{node.openCV.installationDirectory} -D BUILD_PYTHON_SUPPORT=ON ..
    make
    make install
    export LD_LIBRARY_PATH= #{node.openCV.installationDirectory}/lib/:$LD_LIBRARY_PATH
    ldconfig
    EOH
end