class repo_dependencies::python_dependencies {

    # Need pip in order to install python dependencies
    package { "python-pip":
        ensure => present,
    }

    # Needed by pymongo conpilation
    package { "python-dev":
         ensure => present,
    }

    # Needed by bjoern backend for bottle framework
    # (a highly async server written in C)
    package { "libev-dev":
         ensure => present,
    }

    exec { "install-python-packages":
        command => '/usr/bin/pip install -r python_requirements.txt',
        cwd => '/home/ami/AmI-Platform',
        # numpy takes a while to install :)
        timeout => 0
    }

    Package["python-pip"] -> Exec["install-python-packages"]
    Package["python-dev"] -> Exec["install-python-packages"]
    Package["libev-dev"] -> Exec["install-python-packages"]

}
