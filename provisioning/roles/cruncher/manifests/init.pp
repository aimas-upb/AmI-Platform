class cruncher {

    class { "repo_dependencies": }

    package { "upstart":
        ensure => present
    }

    package { "monit":
        ensure => present
    }
}
