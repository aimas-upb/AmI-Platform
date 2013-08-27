user { "ami":
    ensure     => present,
    managehome => true,
    shell	   => '/bin/bash',
}

->

package { "git":
    ensure => present,
}

->

vcsrepo { "/home/ami/AmI-Platform":
    ensure   => present,
    provider => git,
    source   => "git://github.com/ami-lab/AmI-Platform.git",
    user     => "ami",
}

