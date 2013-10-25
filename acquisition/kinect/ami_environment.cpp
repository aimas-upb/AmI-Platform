#include "ami_environment.h"
#include <stdlib.h>
#include <stdio.h>

std::string g_kestrelServerIp;
std::string g_sensorPosition;
std::string g_sensorId;
std::string g_configXmlFile;
int g_kestrelServerPort;


char* getenv(const std::string& var) {
  return getenv(var.c_str());
}

void initEnvironment(std::string envSuffix) {
  if (envSuffix != "") envSuffix = std::string("_") + envSuffix;
  printf("Environment suffix is: %s\n", envSuffix.c_str());
  char *result = getenv(std::string("AMI_KESTREL_SERVER_IP") + envSuffix);
  g_kestrelServerIp = (result == NULL) ? "ami-crunch-01.local" : g_kestrelServerIp = result;

  result = getenv(std::string("AMI_KESTREL_SERVER_PORT") + envSuffix);
  g_kestrelServerPort = (result == NULL) ?  22133 : atoi(result);

  result = getenv(std::string("AMI_SENSOR_POSITION") + envSuffix);
  g_sensorPosition = (result == NULL) ?  "{\"X\": 0.0, \"Y\": 0.0, \"Z\": 0.0, "
               "\"alpha\": 0.0, \"beta\": 0.0, \"gamma\": 0.0}"
    : result;

  // gets value of AMI_SENSOR_ID env variable
  // set in ~/.pam_environment
  char* sensor_id = getenv(std::string("AMI_SENSOR_ID") + envSuffix);
  g_sensorId = (sensor_id == NULL) ? "anonymous" : sensor_id;

  char* config = getenv(std::string("AMI_KINECT_CONFIG_XML") + envSuffix);
  g_configXmlFile = (config == NULL) ? "/home/ami/AmI-Platform/acquisition/kinect/SamplesConfig.xml": config;
}

const char* getKestrelServerIP() {
  return g_kestrelServerIp.c_str();
}

int getKestrelServerPort() {
  return g_kestrelServerPort;
}

const char* getSensorPosition() {
  return g_sensorPosition.c_str();
}

const char* getSensorID() {
  return g_sensorId.c_str();
}

const char* getKinectXMLConfig() {
  return g_configXmlFile.c_str();
}

