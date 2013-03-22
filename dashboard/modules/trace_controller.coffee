define ['cs!controller'], (Controller) ->

    class TraceController extends Controller

        action: ->
            channels_params =
                '/latest_subject_positions': {'sensor_id': 'daq-01'}
            [latest_subject_positions_kinect1] = Utils.newDataChannels(channels_params)

            channels_params =
                '/latest_subject_positions': {'sensor_id': 'anonymous'}
            [latest_subject_positions_kinect2] = Utils.newDataChannels(channels_params)

            channels_params =
                '/latest_subject_positions': {'sensor_id': 'daq-02'}
            [latest_subject_positions_kinect3] = Utils.newDataChannels(channels_params)

            channels_params =
                '/latest_subject_positions': {'sensor_id': 'daq-03'}
            [latest_subject_positions_kinect4] = Utils.newDataChannels(channels_params)

            channels_params =
                '/latest_subject_positions': {'sensor_id': 'daq-04'}
            [latest_subject_positions_kinect5] = Utils.newDataChannels(channels_params)

            channels_params =
                '/latest_subject_positions': {'sensor_id': 'daq-05'}
            [latest_subject_positions] = Utils.newDataChannels(channels_params)

            params =
                latest_subject_positions:
                    channels:
                        '/kinect1': latest_subject_positions_kinect1
                        '/kinect2': latest_subject_positions_kinect2
                        '/kinect3': latest_subject_positions_kinect3
                        '/kinect4': latest_subject_positions_kinect4
                        '/kinect5': latest_subject_positions_kinect5
            @renderLayout(params)
