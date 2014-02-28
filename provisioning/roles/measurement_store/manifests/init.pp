class measurement_store {

 	class { 'mongodb::globals': 
 		manage_package_repo => true,
 	}
    class { 'mongodb': bind_ip => ['0.0.0.0']}

}
