define ['cs!widget'], (Widget) ->

    class ImageWidget extends Widget

        template_name: 'templates/image.hjs'
        subscribed_channels: ['/image', '/skeleton']

        get_image: (params) =>
            ###
                This gets called whenever there is a change
                in the image that has to be displayed.
            ###

            return unless params.type == 'change'
            @last_image = params.model
            @drawImageAndSkeleton()

        get_skeleton: (params) =>
            ###
                This gets called whenever there is a change
                in the image that has to be displayed.
            ###

            return unless params.type == 'change'
            @last_skeleton = params.model
            # @drawImageAndSkeleton()

        drawSkeletonLine: (joint1, joint2, context_2d) =>
            joint1_coords = @last_skeleton.get("skeleton_2d/#{joint1}")
            joint2_coords = @last_skeleton.get("skeleton_2d/#{joint2}")
            if (joint1_coords? && joint2_coords?)
                context_2d.beginPath()
                context_2d.moveTo(parseInt(joint1_coords['X']), parseInt(joint1_coords['Y']))
                context_2d.lineTo(parseInt(joint2_coords['X']), parseInt(joint2_coords['Y']))
                context_2d.stroke()

        drawSkeleton: (context_2d) =>
            ###
                Draw the skeleton from the kinect.
            ###
            @drawSkeletonLine('head', 'neck', context_2d)
            @drawSkeletonLine('neck', 'left_shoulder', context_2d)
            @drawSkeletonLine('neck', 'right_shoulder', context_2d)
            @drawSkeletonLine('left_shoulder', 'left_elbow', context_2d)
            @drawSkeletonLine('right_shoulder', 'right_elbow', context_2d)
            @drawSkeletonLine('left_elbow', 'left_hand', context_2d)
            @drawSkeletonLine('right_elbow', 'right_hand', context_2d)
            @drawSkeletonLine('neck', 'torso', context_2d)
            @drawSkeletonLine('torso', 'left_hip', context_2d)
            @drawSkeletonLine('torso', 'right_hip', context_2d)
            @drawSkeletonLine('left_hip', 'left_knee', context_2d)
            @drawSkeletonLine('right_hip', 'right_knee', context_2d)
            @drawSkeletonLine('left_knee', 'left_foot', context_2d)
            @drawSkeletonLine('right_knee', 'right_foot', context_2d)

        drawImageAndSkeleton: =>

            if not @last_image?
                return

            image_data = "data:image/jpeg;base64," + @last_image.get('image_rgb/image')

            # Avoid bad results due to out of sync system clock
            measured_at = Math.min(new Date().getTime() / 1000 - 1,
                                   @last_image.get('created_at'))
            measured_at_text = moment.unix(measured_at).format('MMMM Do YYYY, h:mm:ss a')

            @renderLayout({'image_data': image_data, 'measured_at': measured_at_text})
