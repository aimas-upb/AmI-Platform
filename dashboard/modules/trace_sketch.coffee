define ['cs!widget/sketch'], (Sketch) ->

    class TraceSketch extends Sketch

        subscribed_channels: ['/kinect1', '/kinect2', '/kinect3',
                              '/kinect4', '/kinect5']

        aggregated_channels: {get_latest_subject_positions:
                               ['/kinect1', '/kinect2', '/kinect3',
                                '/kinect4', '/kinect5']}

        # Viewport dimensions: the room is supposed to be WIDTH x HEIGHT
        # in room coordinates, with a border around in order to account for
        # cases when Kinect coordinates are a little off.
        WIDTH: 941
        HEIGHT: 485
        BORDER_X: 25
        BORDER_Y: 25

        # Size of the rectangle which represents a kinect
        KINECT_SIZE: 25

        # Max & min point size - for the most recent & oldest points
        MAX_POINT_SIZE: 15
        MIN_POINT_SIZE: 5

        # We don't display points who are older than this on the screen
        MAX_POINT_AGE: 30 # seconds

        initialize: =>
            super(arguments...)
            @trajectories = {}

        get_latest_subject_positions: =>
            ###
                Callback that is ran each time we receive data for ANY of the
                kinects. It saves the data for later use by the sketch draw()
                method.
            ###
            COLORS = [Constants.RED, Constants.PURPLE, Constants.BLUE,
                      Constants.GREEN, Constants.ORANGE]

            for idx, kinect_params of arguments
                if kinect_params.type != 'change'
                    continue

                trajectory = kinect_params.model.get('data')
                @trajectories[idx] =
                    points: (JSON.parse(x) for x in trajectory)
                    color: COLORS[idx]

        toScreenCoords: (point) ->
            ###
                Convert a 3D point from room coordinates to screen coordinates.
            ###
            return [@widget.BORDER_X + Math.floor(point['X'] / 10),
                    @widget.BORDER_Y + Math.floor(point['Z'] / 10)]

        setup: ->
            @frameRate(25)
            @size(@widget.WIDTH + 2 * @widget.BORDER_X,
                  @widget.HEIGHT + 2 * @widget.BORDER_Y)
            @colorMode(@RGB, 255)

        drawRoomWalls: ->
            ###
                Draw a schematic of the room walls.
            ###
            @stroke(0)
            @rect(@widget.BORDER_X, @widget.BORDER_Y,
                  @widget.WIDTH-1, @widget.HEIGHT-1)

        drawKinect: (trajectory, drawing_color) ->
            ###
                Given a trajectory, draw the kinect that has captured it.

                We get the coordinates by examining the 'sensor_position'
                key for the first point in the trajectory.
            ###
            if _.isEmpty(trajectory)
                return
            [x, y] = @toScreenCoords(trajectory[0].sensor_position)
            @fill(drawing_color...)
            @rect(x - @widget.KINECT_SIZE / 2,
                  y - @widget.KINECT_SIZE / 2,
                  @widget.KINECT_SIZE, @widget.KINECT_SIZE)

        drawTrajectory: (trajectory, drawing_color) ->
            ###
                Given a trajectory with multiple points, draw them on the
                screen while keeping the most recent points bigger and
                skipping drawing completely for really old points (older than
                30 seconds).
            ###
            now = Utils.now()
            @fill(drawing_color...)
            @prevPoint = null

            for point in trajectory
                # Skip the point completely if it's too old
                created_at = parseInt(point['created_at']) / 1000.0
                age = Math.max(now - created_at, 0) # Account for future points
                if age > @widget.MAX_POINT_AGE
                    continue

                # Compute point size based on its age.
                size = @widget.MAX_POINT_SIZE - (@widget.MAX_POINT_SIZE - @widget.MIN_POINT_SIZE) * age / 30.0

                # Draw a circle for the current point
                [x, y] = @toScreenCoords(point)
                @ellipse(x, y, size, size)

                # The purpose of the line from the previous point to this one
                # is to make it more obvious if we're sampling measurements
                # too rarely for some time intervals and sensors. It will
                # display a big long line which looks nasty in this case :)
                if @prevPoint and Math.abs(created_at - @prevPoint.created_at) < 2
                    @line(@prevPoint.x, @prevPoint.y, x, y)
                @prevPoint = {x: x, y: y, created_at: created_at}
            @noFill()

        draw: ->
            @background(255, 255, 255)
            @drawRoomWalls()
            for idx, {'points': trajectory, 'color': color} of @widget.trajectories
                @drawKinect(trajectory, color)
                @drawTrajectory(trajectory, color)
