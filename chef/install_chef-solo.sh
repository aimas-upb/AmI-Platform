#Add Opscode repository

AMI_PLATFORM_SITE="`pwd`"

echo "deb http://apt.opscode.com/ `lsb_release -cs`-0.10 main" | sudo tee /etc/apt/sources.list.d/opscode.list

#Add GPG Key
sudo mkdir -p /etc/apt/trusted.gpg.d
gpg --keyserver keys.gnupg.net --recv-keys 83EF826A
gpg --export packages@opscode.com | sudo tee /etc/apt/trusted.gpg.d/opscode-keyring.gpg > /dev/null

#Update all packages
sudo apt-get update -y
sudo apt-get install opscode-keyring -y # permanent upgradeable keyring
sudo apt-get upgrade -y


#Install chef
sudo apt-get install chef -y
#Install ruby & dependencies.
sudo apt-get install ruby ruby-dev libopenssl-ruby rdoc ri irb build-essential wget ssl-cert curl -y

#Install ruby gems
cd /tmp
curl -O http://production.cf.rubygems.org/rubygems/rubygems-1.8.10.tgz
tar zxf rubygems-1.8.10.tgz
cd rubygems-1.8.10
sudo ruby setup.rb --no-format-executable

#Install Chef Gem
sudo gem install chef --no-ri --no-rdoc

#Stop chef-client
sudo service chef-client stop

sudo cp $AMI_PLATFORM_SITE/conf/chef/solo.rb /etc/chef/solo.rb