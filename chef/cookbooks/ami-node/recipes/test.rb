script "test" do
	interpreter "bash"
	code <<-EOH
	echo #{node.node_type}
	EOH
end
