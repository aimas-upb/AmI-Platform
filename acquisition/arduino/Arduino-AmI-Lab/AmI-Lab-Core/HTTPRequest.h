/*
 * HTTPRequest.h
 *
 *  Created on: 04.04.2013
 *      Author: Happy
 */

#ifndef HTTPREQUEST_H_
#define HTTPREQUEST_H_

enum HTTPMessageType
{
	GET,
	POST,
	UNKNOWN
};

class HTTPRequest {
public:
	bool valid;
	HTTPMessageType type;
	char command[50];

	HTTPRequest();
	bool ValidateMessage(const char* msg);
	const char* ReponseMessage(const char *msg);

	virtual ~HTTPRequest();

private:
	HTTPMessageType setType(const char* msg);

};

#endif /* HTTPREQUEST_H_ */
