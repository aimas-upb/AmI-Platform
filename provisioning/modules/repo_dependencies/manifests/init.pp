class repo_dependencies {

    class { "repo_dependencies::python_dependencies": }

    ->

    # This needs to be ran after python_dependencies because of python-dev
    # TODO(andrei): find sane way of fixing this
    class { "repo_dependencies::daq_dependencies": }

}
