class repo_dependencies {

    class { "repo_dependencies::python_dependencies": }
    class { "repo_dependencies::opencv": }
    class { "repo_dependencies::daq_dependencies": }

}
