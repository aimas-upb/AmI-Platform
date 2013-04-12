
#include "arduino.h"
#include "core-start.h"
#include "WiFly.h"
#include "WiFlyClient.h"
#include "credentials.h"
#include <string.h>
#include "pin_configuration.h"
#include "SHT1x.h"

#define MAX_SIZE_MESSAGE 128
WiFlyServer server(80);
SHT1x temp_sensor(SHT15_DATA_PIN,SHT15_SCK_PIN );

char message[MAX_SIZE_MESSAGE];
void setup()
{

	Serial.begin(9600);
	Serial.println("Initializing...");
	WiFly.begin(true);
	/*
	while(!SpiSerial.uartConnected())
		SpiSerial.configureUart(9600);
	*/
	Serial.println("Connected to SPI Uart!");

	if(WiFly.createAdHocNetwork("arduino"))
	//if(WiFly.join(ssid, pass, true))
	{

		Serial.print(F("WiFly created AdHoc. Has IP "));
		Serial.println(WiFly.ip());
	}
	else
		Serial.println(F("Failed to create netowrk"));
	analogReference(DEFAULT);
	pinMode(SHT15_DATA_PIN, INPUT);
	pinMode(SHT15_SCK_PIN, OUTPUT);

	pinMode(ANALOG_MIC, INPUT);
	pinMode(ANALOG_LIGHT, INPUT);
	pinMode(ANALOG_SHARP, INPUT);
	/*
if(!WiFly.join("dlink"))
	Serial.println("Could not join network!");
else
	Serial.println(WiFly.ip());
*/
}

void loop()
{
	//char* message;

	WiFlyClient client = server.available();
	if(client)
	{
		Serial.println( "Client available...");
		boolean current_line_is_blank = true;
		message[0] ='\0';
		HTTPRequest req;
		while(client.connected())
		{
			//Serial.println( "Client connected...");
			if (client.available())
			{
					char c = client.read();
					if(c != '\n')
					{
						int len = strlen(message);
						if(len < MAX_SIZE_MESSAGE)
						{
							message[len] = c;
							message[len+1] = '\0';
						}
					}
					// if we've gotten to the end of the line (received a newline
			        // character) and the line is blank, the http request has ended,
			        // so we can send a reply
			        if (c == '\n' && current_line_is_blank) {
			        	req.ValidateMessage(message);
			        	Serial.println(req.type);
			        	Serial.print(message);
			        	Serial.println();
			          // send a standard http response header
			        	Serial.println("Returning response header");
			          client.println("HTTP/1.1 200 OK");
			          client.println("Content-Type: text/html");
			          client.print("\n");
			          printValuesAsJSON();

			          /*
			          client.println("<html><body>");
			          client.print("<p>SHT Temperature:");
			          client.print(temp_sensor.readTemperatureC());
			          client.print("</p><p>SHT Humidity:");
			          client.print(temp_sensor.readHumidity());
			          client.print("</p><p>Luminosity Data:");
			          client.print(analogRead(LIGHT_DATA_PIN));
			          client.print("</p><p>Mic Data:");
			          client.print(analogRead(MIC_DATA_PIN));
			          client.print("</p><p>SHARP Data:");
			          client.print(analogRead(SHARP_DATA_PIN));
			          client.println("</p></body></html>");*/

			          break;
			        }
			        if (c == '\n') {
			          // we're starting a new line
			          current_line_is_blank = true;
			        } else if (c != '\r') {
			          // we've gotten a character on the current line
			          current_line_is_blank = false;
			        }
			}
		}
		delay(100);
		client.stop();
		Serial.println("Client killed");
	}

}

	void printValuesAsJSON()
	{
    client.print("{\"sensor_type\":\"arduino\" , ");
    	  client.print("\"sensor_id\": 0 ,");
    	  client.print("\"data\": {");
    	  	  client.print("\"temperature\":");
    	  	  client.print(temp_sensor.readTemperatureC());
    	  	  client.print(",");
    	  	  client.print("\"luminosity\":");
    	  	  client.print(analogRead(LIGHT_DATA_PIN));
    	  	  client.print(",");
    	  	  client.print("\"sharp_data\" :");
    	  	  client.print(analogRead(SHARP_DATA_PIN));
    	  client.print("}");
    client.print("}");
	}
}





