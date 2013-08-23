class measurement_store {

    class { 'mongodb':
        enable_10gen => true,
    }

}
