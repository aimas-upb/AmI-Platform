class measurement_store {

 	class { 'mongodb::globals': 
 		manage_package_repo => true,
 		bind_ip => '0.0.0.0'
 	}
    class { 'mongodb':}

}
