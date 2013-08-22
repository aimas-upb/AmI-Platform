class repo_dependencies::python_dependencies {

    # Need pip in order to install python dependencies
    package { "python-pip":
        ensure => present,
    }

    # Needed by pymongo conpilation
    package { "python-dev":
         ensure => present,
    }

    exec { "install-python-packages":
        command => '/usr/bin/pip install -r python_requirements.txt',
        cwd => '/home/ami/AmI-Platform',
    }

    Package["python-pip"] -> Exec["install-python-packages"]
    Package["pyhon-dev"] -> Exec["install-python-packages"]

}
