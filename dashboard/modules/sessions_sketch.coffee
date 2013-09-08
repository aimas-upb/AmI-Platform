define ['cs!widget/trace_sketch'], (TraceSketch) ->

    class SessionsSketch extends TraceSketch

        # Viewport dimensions: the room is supposed to be WIDTH x HEIGHT
        # in room coordinates, with a border around in order to account for
        # cases when Kinect coordinates are a little off.
        WIDTH: 640
        HEIGHT: 480

        subscribed_channels: ['/sessions']

        initialize: =>
            super(arguments...)
            @sessions = {}

        get_sessions: (sessions_params) =>
            ###
                Callback that is ran each time we receive data for the sessions.
                It saves the data in a compatible format with the base class
                method drawTrajectory() for later use by the sketch draw()
                method.
            ###
            return unless sessions_params.type == 'change'
            raw_sessions = sessions_params.model.get('sessions')
            @sessions = {}
            for session_id, session_data of raw_sessions
                @sessions[session_id] = []
                for measurement in session_data
                    @sessions[session_id].push(
                        X: measurement.X
                        Y: measurement.Y
                        Z: measurement.Z
                        created_at: measurement.time
                    )

        setup: ->
            super(arguments...)
            @courier_new = @loadFont("Courier New")
            @textFont(@courier_new, 30)

        draw: ->
            @background(255, 255, 255)
            @drawRoomWalls()

            @stroke(0)
            @text("Number of sessions: #{_.keys(@widget.sessions).length}", 200, 30 + @widget.BORDER_Y)

            COLORS = [Constants.RED, Constants.PURPLE, Constants.BLUE,
                      Constants.GREEN, Constants.ORANGE]
            idx = 0
            for session_id, trajectory of @widget.sessions
                color = COLORS[idx % 5]
                @drawTrajectory(trajectory, color)
                idx = idx + 1
