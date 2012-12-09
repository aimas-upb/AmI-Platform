#include "ami_environment.h"
#include <stdlib.h>

char* getKestrelServerIP() {
	char *result = getenv("AMI_KESTREL_SERVER_IP");
	if (result == NULL)
		return "127.0.0.1";
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