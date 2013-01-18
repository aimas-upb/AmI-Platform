python_pip "pykestrel" do
    action :install
end

python_pip "bottle" do
	version "0.11.4"
	action :install
end
python_pip "pymongo" do
	version "2.3"
	action :install
end
python_pip "httplib2" do
	version "0.7.2"
	action :install
end
python_pip "simplejson" do
	version "2.3.2"
	action :install
end
python_pip "Jinja2" do
	version "2.6"
	action :install
end
