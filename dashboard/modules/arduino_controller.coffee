define ['cs!controller'], (Controller) ->
	
	class ArduinoController extends Controller

	   action: ->
            channels_params =
                '/last_arduino_measurement': {'sensor_id': '100', 'measurement_type': 'TEMPERATURE'}
            [last_arduino_temperature_1] = Utils.newDataChannels(channels_params)

            params =
                last_arduino_measurement:
                    channels:
                        '/temperature_1' : last_arduino_temperature_1
            @renderLayout(params)