define ['cs!controller'], (Controller) ->

    class MeasurementsController extends Controller

        action: (session_type, sid, time) ->
            channels_params =
                '/measurements':
                    session_type: session_type
                    sid: sid
                    time: time                  
                      
            [measurements] = Utils.newDataChannels(channels_params)
            
            params =
                measurements:
                    channels:
                      '/measurements': measurements                
                                                
            @renderLayout(params)