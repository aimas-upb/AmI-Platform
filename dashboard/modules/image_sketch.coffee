define ['cs!widget/sketch'], (Sketch) ->

    class ImageSketch extends Sketch

        subscribed_channels: ['/image']

        get_image: (params) =>
            ###
                This gets called whenever there is a change
                in the image that has to be displayed.
            ###
            return unless params.type == 'change'
            image_data = "data:image/jpeg;base64," + params.model.get('image_rgb/image')
            @kinect_image = @processing.loadImage(image_data)

        setup: ->
            @frameRate(5)
            @size(640, 480)
            @colorMode(@RGB, 255)

        draw: ->
            @image(@widget.kinect_image, 0, 0, 640, 480)
