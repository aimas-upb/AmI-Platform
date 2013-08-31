class repo_dependencies::daq_dependencies {

    # Needed by ami-sensor-kinect
    package { "libmemcached-dev":
        ensure => present,
    }

    ->

    package { "g++":
        ensure => present,
    }

    ->

    package { "make":
        ensure => present,
    }

    ->

    package { "cmake":
        ensure => present,
    }

    ->

    package { "freeglut3-dev":
        ensure => present,
    }

    ->

    package { "libusb-1.0.0-dev":
        ensure => present,
    }

    ->

    package { "libboost-python-dev":
        ensure => present,
    }

    ->

    package { "libopencv-dev":
        ensure => present,
    }

    ->

    package { "libcv-dev":
        ensure => present,
    }

    ->

    package { "libhighgui-dev":
        ensure => present,
    }

    ->

    package { "python-dev":
        ensure => present,
    }

    ->

    package { "unzip":
        ensure => present,
    }

    ->

    wget::fetch { "download_openni_binaries":
        source      => "http://www.openni.org/wp-content/uploads/2012/12/OpenNI-Bin-Dev-Linux-x64-v1.5.4.0.tar.zip",
        destination => "/tmp/OpenNI-Bin-Dev-Linux-x64-v1.5.4.0.tar.zip",
    }

    ->

    exec { "unpack_openni_step1":
        command => "/usr/bin/unzip /tmp/OpenNI-Bin-Dev-Linux-x64-v1.5.4.0.tar.zip",
        cwd => "/tmp"
    }

    ->

    exec { "unpack_openni_step2":
        command => "/bin/tar -xjvf /tmp/OpenNI-Bin-Dev-Linux-x64-v1.5.4.0.tar.bz2",
        cwd => "/tmp"
    }

    ->

    file { "/tmp/OpenNI-Bin-Dev-Linux-x64-v1.5.4.0/install.sh":
        mode => "0755",
    }

    ->

    exec { "install_openni":
        command => "/bin/bash /tmp/OpenNI-Bin-Dev-Linux-x64-v1.5.4.0/install.sh",
        cwd => "/tmp/OpenNI-Bin-Dev-Linux-x64-v1.5.4.0"
    }

}
