var App = App || {};

App.DataSourceConfig = {
        channel_types: {
            '/latest_kinect_rgb': {
                type: 'api',
                url: App.general.FRONTEND_URL + '/latest_kinect_rgb/{{sensor_id}}',
                refresh: 'periodic',
                refresh_interval: 10000
            },
            '/latest_kinect_skeleton': {
                type: 'api',
                url: App.general.FRONTEND_URL + '/latest_kinect_skeleton/{{sensor_id}}',
                refresh: 'periodic',
                refresh_interval: 10000
            },
            '/latest_subject_positions': {
                type: 'api',
                url: App.general.FRONTEND_URL + '/latest_subject_positions/{{sensor_id}}',
                refresh: 'periodic',
                refresh_interval: 1
            },
        },
};
