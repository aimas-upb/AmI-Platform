# Start everything script

# Read the list of services and start them
while read -r service_name; do
	echo "===================================================="
	echo "      Starting service $service_name             "
	echo "===================================================="
	echo ""
	sudo service $service_name start
done < services.txt
