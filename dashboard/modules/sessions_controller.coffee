define ['cs!controller'], (Controller) ->

    class SessionsController extends Controller

        action: ->
            [raw_sessions] = Utils.newDataChannels({'/sessions': {'type': 'raw'}})
            [processed_sessions] = Utils.newDataChannels({'/sessions': {'type': 'processed'}})

            params =
                raw_session_store_params:
                    channels:
                        '/sessions': raw_sessions
                processed_session_store_params:
                    channels:
                        '/sessions': processed_sessions

            @renderLayout(params)
