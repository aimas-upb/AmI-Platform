/*
 * HTTPRequest.cpp
 *
 *  Created on: 04.04.2013
 *      Author: Happy
 */

#include "HTTPRequest.h"
#include "string.h"


HTTPRequest::HTTPRequest() {
	// TODO Auto-generated constructor stub

}
bool HTTPRequest::ValidateMessage(const char* msg)
{

	///Set get the type of the message
	this->type = setType(msg);
	if(type == UNKNOWN)
		valid = false;
	else
		valid = true;
	return valid;
}
HTTPRequest::~HTTPRequest() {
	// TODO Auto-generated destructor stub
}


HTTPMessageType HTTPRequest::setType(const char* msg)
{retreive data via http request
	if(strstr(msg, "GET") != NULL)
		return GET;
	if(strstr(msg, "POST") != NULL)
		return POST;
	return UNKNOWN;
}

