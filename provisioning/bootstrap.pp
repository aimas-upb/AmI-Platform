user { "ami":
    ensure     => present,
    managehome => true,
}

package { "git":
    ensure => present,
}

vcsrepo { "/home/ami/AmI-Platform":
    ensure   => present,
    provider => git,
    source   => "git@github.com:ami-lab/AmI-Platform.git",
    user     => "ami",
    require  => Package["git"], User["ami"],
}
