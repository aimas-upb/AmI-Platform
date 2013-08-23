class kestrel ($max_ram='1024m') {

    include wget

    # Kestrel needs java
    package {"openjdk-7-jre-headless":
        ensure => present
    }

    ->

    wget::fetch { "download_kestrel_tarball":
        source  => "http://robey.github.io/kestrel/download/kestrel-2.4.1.zip",
        destination => "/usr/local/kestrel-2.4.1.zip"
    }

    ->

    package { "unzip":
        ensure => present
    }

    ->

    exec { "unzip_kestrel_archive":
        command => "/usr/bin/unzip kestrel-2.4.1.zip",
        cwd => "/usr/local"
     }

    ->

    file { "/usr/local/kestrel":
        ensure => "directory"
    }

    ->

    file { "/usr/local/kestrel/current":
        ensure => "link",
        target => "/usr/local/kestrel-2.4.1"
     }
    ->

    file { "/bin/java":
        ensure => "link",
        target => "/usr/bin/java"
    }

    ->

    file { "/var/run/kestrel":
        ensure => "directory"
    }

    ->

    file { "/var/log/kestrel":
        ensure => "directory"
    }

    ->

    file { "/etc/init.d/kestrel":
        ensure => present,
        content => template('kestrel/kestrel.erb'),
        notify => Service["kestrel"],
        mode => '0755'
    }

    ->

    file { "/usr/local/kestrel-2.4.1.zip":
       ensure => absent
    }

    ->

    service { "kestrel":
        ensure => running
    }

}
