define ['cs!widget'], (Widget) ->
    
    class TraceWidget extends Widget

        MIN_SIZE = 1
        MAX_SIZE = 10

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

            @canvas = @view.$el.find('canvas').get(0)
            @canvas.getContext('2d').fillStyle = Constants.BLACK;
            @canvas.getContext('2d').strokeRect(0, 0, @canvas.width, @canvas.height)

            # draw kinects on dashboard trace
            kinect_side = 20;
            # daq-01
            @canvas.getContext('2d').fillStyle = Constants.RED;
            @canvas.getContext('2d').fillRect(@canvas.width/3, @canvas.height-kinect_side, kinect_side, kinect_side)
            # daq-02
            @canvas.getContext('2d').fillStyle = Constants.PURPLE;
            @canvas.getContext('2d').fillRect(0, @canvas.height*2/3, kinect_side, kinect_side)
            # daq-03
            @canvas.getContext('2d').fillStyle = Constants.BLUE;
            @canvas.getContext('2d').fillRect(@canvas.width/3, 0, kinect_side, kinect_side)
            # daq-04
            @canvas.getContext('2d').fillStyle = Constants.GREEN;
            @canvas.getContext('2d').fillRect(@canvas.width-kinect_side, @canvas.height/3, kinect_side, kinect_side)
            # daq-05
            @canvas.getContext('2d').fillStyle = Constants.ORANGE;
            @canvas.getContext('2d').fillRect(@canvas.width-kinect_side, @canvas.height*2/3, kinect_side, kinect_side)

            @temp_canvas = document.createElement("canvas")
            @temp_canvas.width = @canvas.width
            @temp_canvas.height = @canvas.height

        get_latest_subject_positions: (kinect_params...) =>
            ###
                This gets called whenever there is a change
                in the trace that has to be displayed.
            ###
            @trace_params = kinect_params[0].model
            _.extend(@trace_params, kinect_params[1].model)
            _.extend(@trace_params, kinect_params[2].model)
            _.extend(@trace_params, kinect_params[3].model)
            _.extend(@trace_params, kinect_params[4].model)

            @drawTrace()

        drawTrace: () =>
            ###
                Draws the image with the subjects'traces.
            ###
            if not @trace_params.data?
                return
            if not @trace_params.data.data?
                return

            context_2d = @canvas.getContext('2d')
            temp_context_2d = @temp_canvas.getContext('2d')
            temp_context_2d.clearRect(1, 1, @canvas.width-1, @canvas.height-1)

            position_list = @trace_params.data.data
            for position in position_list
                pos = $.parseJSON(position)
                x = Math.floor(pos['X']/10)
                z = Math.floor(pos['Z']/10)
                sensor_id = pos['sensor_id']

                temp_context_2d.fillStyle = getColor(sensor_id)
                size = @getSize(position_list.indexOf(position), position_list.length)
                temp_context_2d.fillRect(x, z, size, size)

            @canvas.getContext('2d').drawImage(@temp_canvas, 0, 0)

        getColor = (sensor_id) =>
            switch sensor_id
                when "daq-01"
                  return Constants.RED
                when "daq-02"
                  return Constants.PURPLE
                when "daq-03"
                  return Constants.BLUE
                when "daq-04"
                  return Constants.GREEN
                when "daq-05"
                  return Constants.ORANGE
                when "anonymous"
                  return Constants.FUCHSIA
                else
                  Constants.BLACK

        getSize: (index, len) =>
            return (index * (MAX_SIZE - MIN_SIZE) + len*MIN_SIZE)/len
