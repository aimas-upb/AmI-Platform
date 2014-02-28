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
    revision => "f/#269-Create-fab-file-version-for-deploying-on-the-ami-lab-servers"
}

->

file { "/home/ami/.ssh":
    ensure => directory,
    owner  => "ami",
    group  => "ami",
    mode   => "0700",
}

->

exec { "copy_authorized_keys":
    command => "/bin/cp /home/ubuntu/.ssh/authorized_keys /home/ami/.ssh"
}

->

file { "/home/ami/.ssh/authorized_keys":
    ensure  => present,
    owner   => "ami",
    group   => "ami",
    mode    => 0700
}

->

file { "/etc/sudoers.d/80-ami":
    ensure  => present,
    owner   => "root",
    group   => "root",
    mode    => "0440",
    content => "ami ALL=(ALL) NOPASSWD:ALL"
}
