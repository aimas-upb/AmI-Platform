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
        ensure => "link",
        target => "/usr/local/kestrel-2.4.1"
     }

    ->

    file { "/etc/init.d/kestrel":
        ensure => present,
        content => template('kestrel.erb'),
        notify => Service["kestrel"]
    }

    ->

    service { "kestrel":
        ensure => running
    }

}
