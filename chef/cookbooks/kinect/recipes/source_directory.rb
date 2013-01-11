directory "kinect_dir" do
    action :create
    mode 0775
    owner "ami"
    path "/home/#{node.user_name}/kinect"
end

directory "src_archives" do
    action :create
    mode 0775
    owner node.user_name
    path "/home/#{node.user_name}/kinect/downloads"
end
