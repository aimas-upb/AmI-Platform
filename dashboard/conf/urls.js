var App = App || {};

// URLs that are available in our app
App.urls = {
	// The TODO list page is mapped to the empty (missing) hashbang
	'latest_subject_positions': {
        'controller': 'TraceController',
        'layout': 'templates/dashboard_trace.hjs'
    },
    '': {
        'controller': 'DashboardController',
        'layout': 'templates/dashboard_page.hjs'
    },
};
