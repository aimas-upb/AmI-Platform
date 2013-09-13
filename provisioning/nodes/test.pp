class test {
    class {"kestrel": }
    
    class { "session_store": }
    # Dashboard API should be close to the Redis it's reading from
    class { "dashboard_api": }
    
    class { "measurement_store": }
}