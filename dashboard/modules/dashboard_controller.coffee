define ['cs!controller'], (Controller) ->

    class DashboardController extends Controller

        action: ->
            channels_params =
                '/latest_kinect_rgb': {'sensor_id': 'daq-01'}
                '/latest_kinect_skeleton': {'sensor_id': 'daq-01'}
            [latest_kinect_rgb, latest_kinect_skeleton] = Utils.newDataChannels(channels_params)

            params =
                latest_kinect_rgb_params:
                    channels:
                        '/image': latest_kinect_rgb
                        '/skeleton': latest_kinect_skeleton

            @renderLayout(params)
