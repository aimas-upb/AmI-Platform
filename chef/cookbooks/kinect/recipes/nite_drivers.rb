remote_file "nite" do
    action :create
    path "/home/ami/kinect/downloads/nite.tar.zip"
    mode 0755
    owner  node.user_name
	source node.nite.remote_src
end


script "extract" do
    interpreter "bash"
    cwd "/home/#{node.user_name}/kinect"
    code <<-EOH
    unzip -o ./downloads/nite.tar.zip -d ./downloads
    tar jxf ./downloads/#{node.nite.extracted_arch}
    mv ./#{node.nite.extracted_folder} ./nite 
    cd ./nite
    chmod a+x install.sh
    sudo ./install.sh
    EOH
end
