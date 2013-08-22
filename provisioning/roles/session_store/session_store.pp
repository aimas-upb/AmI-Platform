class { 'redis':
    # 2.6.14 is the last version of redis available on redis.googlecode.com
    # which is the obsolete mirror used by the thomasvandoren/redis module
    # v0.0.9 on puppetforge (fixed on master, but master isn't published on
    # puppetforge).
    version => '2.6.14',
    redis_bind_address => '0.0.0.0',
    redis_max_memory => '1gb'
}

