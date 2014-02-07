class measurement_store {

 	class { 'mongodb::globals': manage_package_repo => true }
    class { 'mongodb':}

}
