class repo_dependencies::daq_dependencies {

    # Needed by ami-sensor-kinect
    package { "libmemcached-dev":
         ensure => present,
    }

}
