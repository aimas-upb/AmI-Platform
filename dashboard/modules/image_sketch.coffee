define ['cs!widget/sketch'], (Sketch) ->

    class ImageSketch extends Sketch

        subscribed_channels: ['/image']

        get_image: (params) =>
            ###
                This gets called whenever there is a change
                in the image that has to be displayed.
            ###
            return unless params.type == 'change'
            base64_image_data = params.model.get('image_rgb/image')
            if not base64_image_data
                return
            image_data = "data:image/jpeg;base64," + base64_image_data
            @kinect_image = @processing.loadImage(image_data)

        setup: ->
            @frameRate(5)
            @size(640, 480)
            @colorMode(@RGB, 255)

        draw: ->
            return unless @widget.kinect_image?
            @image(@widget.kinect_image, 0, 0, 640, 480)
