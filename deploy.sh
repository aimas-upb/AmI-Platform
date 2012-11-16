# Redeploy everything script

# Get rid of non-committed changes
git reset --hard HEAD

# Get latest changes from repo
git pull origin master

# Make sure that filesystem is in sync with git index
git reset --hard HEAD

# Read the list of services, and copy the new upstart & monit files + restart
while read service_name
	sudo cp ./scripts/upstart/$service_name.conf /etc/init
	sudo cp ./scripts/monit/$service_name /etc/monit/conf.d
	sudo service $service_name restart
do
done < services.txt