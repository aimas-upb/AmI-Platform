# Redeploy everything script

fresh=false

for ((i = 1; $#; i++)); do
    case $1 in
        --fresh) $fresh=true ; shift 1 ;;
        --?*) shift 2 ;;
    esac
done

# If we need fresh code, throw everything away and
# get it from GitHub.
if $fresh; then
	branch=$(git rev-parse --abbrev-ref HEAD)

	# Get rid of non-committed changes
	git reset --hard HEAD

	# Get latest changes from repo
	git pull origin $branch

	# Make sure that filesystem is in sync with git index
	git reset --hard HEAD
fi

# See if there is a host-specific service name
service_name="services.txt"
host_specific_service_name="services.$(hostname -s).txt"
if [ -f $host_specific_service_name]; then
	$service_name=$host_specific_service_name

# Read the list of services, and copy the new upstart & monit files + restart
while read -r service_name; do
	echo "===================================================="
	echo "      Redeploying service $service_name             "
	echo "===================================================="
	echo ""
	echo "Copying new upstart script for service $service_name"
	sudo cp ./scripts/upstart/$service_name.conf /etc/init
	echo "Copying new monit script for service $service_name"
	sudo cp ./scripts/monit/$service_name /etc/monit/conf.d
	echo "Restarting service $service_name"
	sudo service $service_name restart
done < $service_name
