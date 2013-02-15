#include "ami_environment.h"
#include <stdlib.h>

char* getKestrelServerIP() {
	char *result = getenv("AMI_KESTREL_SERVER_IP");
	if (result == NULL)
		return "ami-crunch-01.local";
	else
		return result;
}

int getKestrelServerPort() {
	char *result = getenv("AMI_KESTREL_SERVER_PORT");
	if (result == NULL)
		return 22133;
	else
		return atoi(result);
}

char* getSensorID() {
	// gets value of AMI_SENSOR_ID env variable
	// set in ~/.pam_environment
	char *sensor_id = getenv("AMI_SENSOR_ID");
	if (sensor_id == NULL)
		return "senzor_anonim";
	return sensor_id;
}
