var App = App || {};

// URLs that are available in our app
App.urls = {
    '': {
        'controller': 'SessionsController',
        'layout': 'templates/dashboard_page.hjs'
    },
    'sessions': {
        'controller': 'SessionsController',
        'layout': 'templates/pages/sessions.hjs'
    },
    'latest_subject_positions': {
        'controller': 'TraceController',
        'layout': 'templates/dashboard_trace.hjs'
    },
};
