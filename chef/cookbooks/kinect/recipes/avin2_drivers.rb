remote_file "avin2" do
    action :create
    path "/home/#{node.user_name}/kinect/downloads/avin2.zip" 
    mode 0755
    owner node.user_name
    source node.avin2.remote_src
end


script "extract" do
    interpreter "bash"
    cwd "/home/#{node.user_name}/kinect"
    code <<-EOH
    sudo unzip ./downloads/avin2.zip
    mv ./#{node.avin2.extracted_folder} ./avin2
    cd ./avin2/Platform/Linux/CreateRedist/
    chmod a+x RedistMaker
    sudo ./RedistMaker
    cd ../Redist/#{node.avin2.redist_folder}
    sudo chmod a+x install.sh
    sudo ./install.sh
    EOH
end
