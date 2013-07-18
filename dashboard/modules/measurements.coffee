define ['cs!widget'], (Widget) ->

    class MeasurementsWidget extends Widget

        template_name: 'templates/measurements.hjs'
        subscribed_channels: ['/measurements']

        get_measurements: (params) =>

            return unless params.type == 'change'
            m = params.model
  
            subject_position = m.get('measurements/subject_position')
            head = m.get('measurements/head')

            params = {}
            if subject_position
              params['subject_position'] =
                channels:
                  '/measurements': @channel_mapping['/measurements']
           
            if head
              params['head'] =
                channels:
                  '/measurements': @channel_mapping['/measurements']
             
            time = new Date(m.get('measurements/time'))
            params['time'] = time.toUTCString()

            @renderLayout(params)
            
            
            
