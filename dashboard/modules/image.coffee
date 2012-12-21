define ['cs!widget'], (Widget) ->
    
    class ImageWidget extends Widget

        template_name: 'templates/image.hjs'
        subscribed_channels: ['/image', '/skeleton']
        
        events:
            "click a.save-image": "saveImageToFile"
        
        initialize: =>
            ###
                Create an HTML5 canvas which will be used
                to render the image.
            ###
            @renderLayout()

            # Normally we would use "elements" for this, but we want the
            # raw DOM element instead of the jQuery one.
            @canvas = @view.$el.find('canvas').get(0)
        
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
            @drawImageAndSkeleton()
        
        drawSkeletonLine: (joint1, joint2, context_2d) =>
            joint1_coords = @last_skeleton.get("skeleton_2d/#{joint1}")
            joint2_coords = @last_skeleton.get("skeleton_2d/#{joint2}")
            
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
            width = parseInt(@last_image.get('width'))
            height = parseInt(@last_image.get('height'))
            pixels = context_2d.createImageData(width, height)
            
            # Get the base64-decoded image
            image = @last_image.get('image') 
            decoded_image = atob(image)
            
            # Transfer pixels from the decoded image to canvas
            # buffer. NOTE: canvas also has an alpha channel.
            for x in [0..width-1]
                for y in [0..height-1]
                    index = (y * width + x) * 4
                    index2 = (y * width + x) * 3
                    pixels.data[index] = decoded_image[index2].charCodeAt(0)
                    pixels.data[index + 1] = decoded_image[index2 + 1].charCodeAt(0)
                    pixels.data[index + 2] = decoded_image[index2 + 2].charCodeAt(0)
                    pixels.data[index + 3] = 255
            
            # Render the actual image to HTML
            context_2d.putImageData(pixels, 0, 0)
            
        drawImageAndSkeleton: =>
          
            if not @last_image? or not @last_skeleton?
                return
          
            context_2d = @canvas.getContext('2d')
            @drawImage(context_2d)
          
            # Check if image and skeleton ar at most 1s apart
            image_created_at = parseInt(@last_image.get('created_at'))
            skeleton_created_at = parseInt(@last_skeleton.get('created_at'))
            if Math.abs(image_created_at - skeleton_created_at) >= 2
                console.warn("Skeleton and image probably do not match together (difference >= 2s)")
                return
            
            @drawSkeleton(context_2d)

        saveImageToFile: (event) =>
            urlData = @canvas.toDataURL('image/jpeg')
            window.open(urlData, 'Save image to file')
