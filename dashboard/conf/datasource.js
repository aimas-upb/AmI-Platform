var App = App || {};

App.DataSourceConfig = {
		channel_types: {
			'/latest_kinect_rgb': {
				type: 'api',
				url: App.general.FRONTEND_URL + '/api/latest_kinect_rgb',
				refresh: 'periodic',
				refresh_interval: 1000
			},
		},
};
