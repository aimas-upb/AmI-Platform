class ami_api($hostname) {

    package {'nginx':
        ensure => present
    }

    ->

    file {'/etc/nginx/sites-available/ami_api':
        ensure  => present,
        content => template('ami_api/api_nginx_vhost.erb'),
        owner   => 'root',
        group   => 'root',
        mode    => '0644'
    }

    ->

    file {'/etc/nginx/sites-enabled/ami_api':
        ensure  => link,
        target  => '/etc/nginx/sites-available/ami_api'
    }

    ~>

    service {'nginx':
        ensure => running
    }

}
