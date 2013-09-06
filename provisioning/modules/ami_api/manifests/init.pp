class ami_api($hostname) {

    package {'nginx':
        ensure => present
    }

    ->

    file {'/etc/nginx/conf.d/ami_api':
        content => template('ami_api/api_vhost.erb')
        owner   => 'root',
        group   => 'root',
        mode    => '0644'
    }

    ~>

    service {'nginx':
        ensure => running
    }

}
