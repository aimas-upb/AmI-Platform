var App = App || {};

App.general = {
    USE_MOCKS: false,
    FRONTEND_URL: 'http://127.0.0.1:8000',
    STATIC_URL: '/static/app',
    LOG_LEVEL: 1000, // Everything
    PAGE_LAYOUT: 'templates/page.hjs',
    ENVIRONMENT: 'testing',
    LOGGER_MODULE: 'standard_logger',

    // Throw exceptions and don't catch them with our wrapper
    // so that we can debug them easier.
    THROW_UNCAUGHT_EXCEPTIONS: true,

    // Don't use precompiled templates
    USE_PRECOMPILED_TEMPLATES: false,

    // JS file to be used as entry-point for the application
    ENTRY_POINT: 'mozaic'
};
// Can't use precompiled templates if not in production
// because the bundle.sh is not run every time and prob
// tpl.js doesn't exist
if (App.general.ENVIRONMENT !== 'production')
    App.general.USE_PRECOMPILED_TEMPLATES = false;

if (typeof module != 'undefined') {
    module.exports.general = App.general;
}
