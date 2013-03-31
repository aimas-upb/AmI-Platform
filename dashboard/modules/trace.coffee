define ['cs!widget'], (Widget) ->
    
    class TraceWidget extends Widget

        BLACK   = "#000000"
        RED     = "#FF0000"
        GREEN   = "#008000"
        BLUE    = "#0000FF"
        PURPLE  = "#800080"
        ORANGE  = "#FFA500"
        FUCHSIA = "#FF00FF"

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
            @canvas.getContext('2d').fillStyle = BLACK;
            @canvas.getContext('2d').strokeRect(0, 0, @canvas.width, @canvas.height)

            @temp_canvas = document.createElement("canvas")
            @temp_canvas.width = @canvas.width
            @temp_canvas.height = @canvas.height

        get_latest_subject_positions: (kinect_params...) =>
            ###
                This gets called whenever there is a change
                in the trace that has to be displayed.
            ###
            # return unless (kinect_params[0].type == 'change' or
                           # kinect_params[1].type == 'change' or
                           # kinect_params[2].type == 'change' or
                           # kinect_params[3].type == 'change' or
                           # kinect_params[4].type == 'change')

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
                x = Math.floor(pos['X']/20)
                z = Math.floor(pos['Z']/20)
                sensor_id = pos['sensor_id']

                temp_context_2d.fillStyle = getColor(sensor_id)
                size = @getSize(position_list.indexOf(position), position_list.length)
                temp_context_2d.fillRect(x, z, size, size)

            @canvas.getContext('2d').drawImage(@temp_canvas, 0, 0)

        getColor = (sensor_id) =>
            switch sensor_id
                when "daq-01"
                  return RED
                when "daq-03"
                  return BLUE
                when "daq-04"
                  return GREEN
                when "daq-05"
                  return ORANGE
                when "daq-06"
                  return PURPLE
                when "anonymous"
                  return FUCHSIA
                else
                  BLACK

        getSize: (index, len) =>
            return (index * (MAX_SIZE - MIN_SIZE) + len*MIN_SIZE)/len
