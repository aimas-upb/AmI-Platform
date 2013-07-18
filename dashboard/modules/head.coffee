define ['cs!widget'], (Widget) ->

    class HeadWidget extends Widget

        template_name: 'templates/head.hjs'
        subscribed_channels: ['/measurements']

        get_measurements: (params) =>
            return unless params.type == 'change'
            m = params.model

            @renderLayout({
              'image_data': m.get('measurements/head/image')
            })
