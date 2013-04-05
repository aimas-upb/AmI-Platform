define ['cs!widget'], (Widget) ->
    
    class TraceWidget extends Widget

        MIN_SIZE = 1
        MAX_SIZE = 10
        KINECT_SIDE = 20

        template_name: 'templates/trace.hjs'
        subscribed_channels: ['/kinect1', '/kinect2', '/kinect3', '/kinect4',
                              '/kinect5', '/kinect6']
        aggregated_channels: {get_latest_subject_positions: ['/kinect1',
                              '/kinect2', '/kinect3', '/kinect4', '/kinect5', '/kinect6']}

        initialize: =>
            ###
                Create an HTML5 canvas which will be used
                to render the subjects' traces.
            ###
            @renderLayout()

            @canvas = @view.$el.find('canvas').get(0)
            @canvas.getContext('2d').fillStyle = Constants.BLACK;
            @canvas.getContext('2d').strokeRect(0, 0, @canvas.width, @canvas.height)

            @drawKinects(@canvas.getContext('2d'))

        get_latest_subject_positions: (kinect_params...) =>
            ###
                This gets called whenever there is a change
                in the trace that has to be displayed.
            ###
            @drawTraces(kinect_params)

        drawTraces: (params) =>
            ###
                Draws the image with the subjects'traces.
            ###
            temp_canvas = document.createElement("canvas")
            temp_canvas.width = @canvas.width
            temp_canvas.height = @canvas.height
            temp_context_2d = temp_canvas.getContext('2d')
            temp_context_2d.fillStyle = Constants.WHITE
            temp_context_2d.fillRect(1, 1, @canvas.width-2, @canvas.height-2)

            @drawTrace(temp_context_2d, params[1].model.data.data) if params[1].model?
            @drawTrace(temp_context_2d, params[2].model.data.data) if params[2].model?
            @drawTrace(temp_context_2d, params[3].model.data.data) if params[3].model?
            @drawTrace(temp_context_2d, params[4].model.data.data) if params[4].model?
            @drawTrace(temp_context_2d, params[5].model.data.data) if params[5].model?

            # TODO (diana): find a solution to avoid redrawing kinects everytime
            @drawKinects(temp_context_2d)
            @canvas.getContext('2d').drawImage(temp_canvas, 0, 0)

        drawTrace: (context, params) =>
            i = 0
            while i < params.length
                pos = $.parseJSON(params[i])
                x = Math.floor(pos['X']/10)
                z = Math.floor(pos['Z']/10)
                size = @getSize(i, params.length)
                context.fillStyle = getColor(pos['sensor_id'])
                context.fillRect(x, z, size, size)
                i++

        drawKinects: (context) =>
            # draw kinects on dashboard trace
            # daq-01
            context.fillStyle = Constants.RED;
            context.fillRect(@canvas.width/3, @canvas.height-KINECT_SIDE, KINECT_SIDE, KINECT_SIDE)
            # daq-02
            context.fillStyle = Constants.PURPLE;
            context.fillRect(0, @canvas.height*2/3, KINECT_SIDE, KINECT_SIDE)
            # daq-03
            context.fillStyle = Constants.BLUE;
            context.fillRect(@canvas.width/3, 0, KINECT_SIDE, KINECT_SIDE)
            # daq-04
            context.fillStyle = Constants.GREEN;
            context.fillRect(@canvas.width-KINECT_SIDE, @canvas.height/3, KINECT_SIDE, KINECT_SIDE)
            # daq-05
            context.fillStyle = Constants.ORANGE;
            context.fillRect(@canvas.width-KINECT_SIDE, @canvas.height*2/3, KINECT_SIDE, KINECT_SIDE)

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
            return MAX_SIZE - (index * (MAX_SIZE-MIN_SIZE)/len)
