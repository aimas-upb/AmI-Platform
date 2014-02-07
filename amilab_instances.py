class Instance(object):
    
    def __init__(self, name):
        self.public_dns_name = name
        self.private_dns_name = name
        self.tags = {}
        
    def matches_tags(self, tags):
        for k, v in tags.iteritems():
            if v != tags.get(k):
                return False
        return True

instances = [Instance('ami-crunch-08.local'), Instance('ami-crunch-09.local')]

def get_instance_by_name(hostname):
    for i in instances:
        if i.public_dns_name == hostname:
            return i
    return None

def get_instances_by_tags(tags):
    return [i for i in instances if i.matches_tags(tags)]  

def get_instance_for_service(service):
    matching = [i for i in instances if service in i.tags.get('services', [])]
    if len(matching) == 1:
        return matching[0]
    print("Instances for service(%s) needs to contain exactly 1 element, found %d" % (service, len(matching)))
    return None

def get_instance_by_tags(tags):
    """ Get a single instance from the EC2 cloud using tags to filter it out.
    Asserts that there is exactly one instance, and returns None when this isn't
    the case. """
    instances = get_instances_by_tags(tags)
    if not instances or len(instances) == 0:
        print("There is no instance matching tags %r" % tags)
        return None

    if len(instances) > 1:
        print("This is confusing .. More than one instance matching %r" %
                     tags)
        return None

    return instances[0]

def get_crunch_running(module_name):
    """ Gets the crunch node running a given module. """
    crunch_hostnames = [instance.public_dns_name for instance in
                        get_instances_by_tags({'type': 'crunch'})]
    for crunch_hostname in crunch_hostnames:
        tags = get_tags_for_machine(crunch_hostname)
        if 'modules' in tags:
            modules = tags['modules'].split(',')
            if module_name in modules:
                return crunch_hostname

    return None


def tag_instance(hostname, machine_meta_data):
    instance = get_instance_by_name(hostname)
    if instance is not None:
        instance.tags.update(machine_meta_data)

def get_tags_for_machine(hostname):
    return get_instance_by_name(hostname).tags

def get_all_instances():
    return instances