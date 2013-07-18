define ['cs!widget'], (Widget) ->

    class SubjectPositionWidget extends Widget

        template_name: 'templates/subject_position.hjs'
        subscribed_channels: ['/measurements']

        get_measurements: (params) =>

            return unless params.type == 'change'
            last_position = params.model

            @renderLayout({              
              'X': last_position.get('measurements/subject_position/X'),
              'Y': last_position.get('measurements/subject_position/Y'),
              'Z': last_position.get('measurements/subject_position/Z')              
            })
