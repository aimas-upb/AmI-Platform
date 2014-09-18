#ifndef __AMI_ENVIRONMENT__
#define __AMI_ENVIRONMENT__

#include <string>

void initEnvironment(std::string g_envSufix);
const char* getKestrelServerIP();
int getKestrelServerPort();
const char* getSensorPosition();
const char* getSensorID();
const char* getKinectXMLConfig();

#endif
