# Redeploy everything script

branch=$(git rev-parse --abbrev-ref HEAD)

# Get rid of non-committed changes
git reset --hard HEAD

# Get latest changes from repo
git pull origin $branch

# Make sure that filesystem is in sync with git index
git reset --hard HEAD

# Read the list of services, and copy the new upstart & monit files + restart
while read service_name
do
	sudo cp ./scripts/upstart/$service_name.conf /etc/init
	sudo cp ./scripts/monit/$service_name /etc/monit/conf.d
	sudo service $service_name restart
done < services.txt
