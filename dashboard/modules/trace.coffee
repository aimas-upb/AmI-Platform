define ['cs!widget'], (Widget) ->
    
    class ImageWidget extends Widget

        template_name: 'templates/trace.hjs'
        subscribed_channels: ['/trace']
        
        initialize: =>
            ###
                Create an HTML5 canvas which will be used
                to render the subjects' traces.
            ###
            @renderLayout()

        get_image: (params) =>
            ###
                This gets called whenever there is a change
                in the trace that has to be displayed.
            ###
            @renderLayout(params)
