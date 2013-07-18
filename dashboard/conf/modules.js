var App = App || {};
// Need to initialize this for the extend method to work in the tests
App.main_modules = App.main_modules || {};

App.the_modules = {
	'widget/head': 'modules/head',
	'widget/image': 'modules/image',
	'widget/measurements': 'modules/measurements',
	'widget/session_store': 'modules/session_store',
	'widget/subject_position': 'modules/subject_position',
	'widget/trace': 'modules/trace',

	'widget/DashboardController': 'modules/dashboard_controller',
	'widget/MeasurementsController': 'modules/measurements_controller',
	'widget/SessionsController': 'modules/sessions_controller',
	'widget/TraceController': 'modules/trace_controller',
};

// This is actually how we check if this is being ran
// in node.js enviromnent, _module_ being an omnipresent
// entity there
if (typeof module != 'undefined') {
    module.exports.main_modules = App.the_modules;
} else {
    for (var k in App.the_modules) {
        App.main_modules[k] = App.the_modules[k];
    }
}
