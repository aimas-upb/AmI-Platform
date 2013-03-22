define ['cs!controller'], (Controller) ->

    class TraceController extends Controller

        subscribed_channels = ['/latest_subject_positions']
        action: ->
            params =
                latest_subject_positions:
                    channels:
                        '/latest_subject_positions': c['/latest_subject_positions']
            @renderLayout(params)
