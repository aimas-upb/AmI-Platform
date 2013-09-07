class code_settings($redis_hostname,
                    $redis_port,
                    $mongo_hostname,
                    $mongo_port,
                    $kestrel_hostname,
                    $kestrel_port) {

    file {'/home/ami/AmI-Platform/dashboard/conf/general.user.js':
        ensure	=> present,
        content => template('code_settings/general_user_js.erb')
        owner   => 'ami',
        group	=> 'ami',
        mode	=> '0644',
    }

    file {'/home/ami/AmI-Platform/core/settings_local.py':
        ensure	=> present,
        content => template('code_settings/settings_local_py.erb')
        owner   => 'ami',
        group	=> 'ami',
        mode	=> '0644',
    }

}
