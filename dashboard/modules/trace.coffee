define ['cs!widget'], (Widget) ->
    
    class ImageWidget extends Widget

        template_name: 'templates/trace.hjs'
        subscribed_channels: ['/kinect1', '/kinect2', '/kinect3', '/kinect4',
                              '/kinect5']
        aggregated_channels: {get_latest_subject_positions: ['/kinect1',
                              '/kinect2', '/kinect3', '/kinect4', '/kinect5']}

        initialize: =>
            ###
                Create an HTML5 canvas which will be used
                to render the subjects' traces.
            ###
            @renderLayout()

        get_latest_subject_positions: (kinect1_paramas, kinect2_paramas, kinect3_params,
                    kinect4_params, kinect5_params) =>
            ###
                This gets called whenever there is a change
                in the trace that has to be displayed.
            ###
            # return union of all received params
            params = {}
            @renderLayout(params)