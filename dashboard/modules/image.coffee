define ['cs!widget'], (Widget) ->

    class ImageWidget extends Widget

        template_name: 'templates/image.hjs'
        subscribed_channels: ['/image', '/skeleton']

        initialize: =>
            ###
                Create an HTML5 canvas which will be used
                to render the image.
            ###
            @renderLayout()

            # Normally we would use "elements" for this, but we want the
            # raw DOM element instead of the jQuery one.
            @canvas = [@view.$el.find('canvas.c1').get(0), @view.$el.find('canvas.c2').get(0)]
            @temp_canvas = document.createElement("canvas")
            @temp_canvas.width = 1280
            @temp_canvas.height = 1024

            @canvas_idx = 1
            $(@canvas[1-@canvas_idx]).show()
            $(@canvas[@canvas_idx]).hide()

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

        drawImage: (context_2d) =>
            ###
                Draw the RGB image from the kinect.
            ###
            width = parseInt(@last_image.get('image_rgb/width'))
            height = parseInt(@last_image.get('image_rgb/height'))
            pixels = context_2d.createImageData(width, height)

            # Get the base64-decoded image
            img = new Image
            img.src = "data:image/jpeg;base64," + @last_image.get('image_rgb/image')
            context_2d.drawImage(img,0,0)

            font_size = 40
            context_2d.font = "#{font_size}px Arial"

            # Avoid bad results due to out of sync system clock
            measured_at = Math.min(new Date().getTime() / 1000 - 1,
                                   @last_image.get('created_at'))
            text = moment.unix(measured_at).format('MMMM Do YYYY, h:mm:ss a')
            text_width = context_2d.measureText(text).width
            context_2d.fillText(text,
                                width - text_width - 20,
                                height - font_size - 20)

        drawImageAndSkeleton: =>

            if not @last_image?
                return

            temp_context_2d = @temp_canvas.getContext('2d')
            temp_context_2d.clearRect(0, 0, @temp_canvas.width, @temp_canvas.height)
            @drawImage(temp_context_2d)

            # Scale down to lower res
            context_2d = @canvas[@canvas_idx].getContext('2d')
            context_2d.clearRect(0, 0, @canvas[@canvas_idx].width, @canvas[@canvas_idx].height)
            context_2d.drawImage(@temp_canvas,
                                 0, 0, @temp_canvas.width, @temp_canvas.height,
                                 0, 0, @canvas[@canvas_idx].width, @canvas[@canvas_idx].height)

            $(@canvas[1 - @canvas_idx]).hide()
            $(@canvas[@canvas_idx]).show()
            @canvas_idx = 1 - @canvas_idx
            
