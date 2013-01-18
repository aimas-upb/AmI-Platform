remote_file "openni" do
    source node.openni.remote_src
	path "/home/#{node.user_name}/kinect/downloads/openni.tar.zip"
    mode 0755
    owner node.user_name
    action :create
end



script "extract" do
    interpreter "bash"
    cwd "/home/#{node.user_name}/kinect"
    code <<-EOH
    unzip ./downloads/openni.tar.zip -d ./downloads
    tar jxf ./downloads/#{node.openni.extracted_arch}
    mv ./#{node.openni.extracted_folder} ./openni
    cd ./openni
    chmod a+x install.sh
    sudo ./install.sh
    EOH
end
