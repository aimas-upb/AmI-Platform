class cruncher {

    class { "repo_dependencies": }

    class { "code_settings": }

    package { "upstart":
        ensure => present
    }

    package { "monit":
        ensure => present
    }
}
