define ['cs!controller'], (Controller) ->

    class DashboardController extends Controller

        action: ->
            channels_params =
                '/latest_kinect_rgb': {'sensor_id': 'daq-01'}
                '/latest_kinect_skeleton': {'sensor_id': 'daq-01'}
            [latest_kinect_rgb_1, latest_kinect_skeleton_1] = Utils.newDataChannels(channels_params)

            channels_params =
                '/latest_kinect_rgb': {'sensor_id': 'daq-02'}
                '/latest_kinect_skeleton': {'sensor_id': 'daq-02'}
            [latest_kinect_rgb_2, latest_kinect_skeleton_2] = Utils.newDataChannels(channels_params)

            channels_params =
                '/latest_kinect_rgb': {'sensor_id': 'daq-03'}
                '/latest_kinect_skeleton': {'sensor_id': 'daq-03'}
            [latest_kinect_rgb_3, latest_kinect_skeleton_3] = Utils.newDataChannels(channels_params)

            channels_params =
                '/latest_kinect_rgb': {'sensor_id': 'daq-04'}
                '/latest_kinect_skeleton': {'sensor_id': 'daq-04'}
            [latest_kinect_rgb_4, latest_kinect_skeleton_4] = Utils.newDataChannels(channels_params)

            channels_params =
                '/latest_kinect_rgb': {'sensor_id': 'daq-05'}
                '/latest_kinect_skeleton': {'sensor_id': 'daq-05'}
            [latest_kinect_rgb_5, latest_kinect_skeleton_5] = Utils.newDataChannels(channels_params)

            params =
                latest_kinect_rgb_params_1:
                    channels:
                        '/image': latest_kinect_rgb_1
                        '/skeleton': latest_kinect_skeleton_1
                latest_kinect_rgb_params_2:
                    channels:
                        '/image': latest_kinect_rgb_2
                        '/skeleton': latest_kinect_skeleton_2
                latest_kinect_rgb_params_3:
                    channels:
                        '/image': latest_kinect_rgb_3
                        '/skeleton': latest_kinect_skeleton_3
                latest_kinect_rgb_params_4:
                    channels:
                        '/image': latest_kinect_rgb_4
                        '/skeleton': latest_kinect_skeleton_4
                latest_kinect_rgb_params_5:
                    channels:
                        '/image': latest_kinect_rgb_5
                        '/skeleton': latest_kinect_skeleton_5

            @renderLayout(params)
