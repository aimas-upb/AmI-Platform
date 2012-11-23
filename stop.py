# Stop everything script

# Read the list of services and stop them
while read -r service_name; do
	echo "===================================================="
	echo "      Stopping service $service_name             "
	echo "===================================================="
	echo ""
	sudo service $service_name stop
done < services.txt
