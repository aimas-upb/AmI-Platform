define ['cs!widget'], (Widget) ->

    class Sketch extends Widget

        params_defaults:
            'sketch': 'data-params'
        params_required: ['sketch']
        template_name: 'templates/sketch.hjs'

        initialize: =>
            @renderLayout()
            canvas = @view.$el.find('canvas').get(0)
            @processing = @runSketchInCanvas(@, canvas)

        destroy: =>
            # Cut off cross-reference between processing instance and widget
            @processing.widget = null
            @processing = null
            super()

        _wrapInstance: ->
            # Overwrite wrapping mechanism so that sketches don't have
            # their methods wrapped in any way. This ensures that
            # thin arrows stay thin arrows.
            return

        runSketchInCanvas: (sketch_instance, canvas) ->
            sketch = new Processing.Sketch(
                (processing) ->
                    for k, v of sketch_instance
                        if _.isFunction(v)
                            bound_instance_fn = _.bind(v, processing)
                            processing[k] = bound_instance_fn
                            @[k] = bound_instance_fn
                    processing.widget = sketch_instance
                    sketch_instance.processing = processing
            )
            processing = new Processing(canvas, sketch)
            return processing
