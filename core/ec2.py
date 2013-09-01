import logging

import boto

logger = logging.getLogger(__name__)

def get_running_instances(reservations):
    """ Given a set of reservations, each of which might contain 0
    or more instances, get the set of running instances (those with
    status == 'running'. """
    if not reservations or len(reservations) == 0:
        return []

    instances = []
    for reservation in reservations:
        for instance in reservation.instances:
            if instance.status == 'running':
                instances.append(instance)
    return instances

def get_instances_by_tags(tags):
    """ Get a set of instances from the EC2 cloud using tags to filter
    them out. """
    ec2 = boto.connect_ec2()
    filters = {}
    for k, v in tags.iteritems():
        filters['tag:%s' % k] = v
    return get_running_instances(ec2.get_all_instances(filters))

def get_instances_by_filters(filters):
    ec2 = boto.connect_ec2()
    return get_running_instances(ec2.get_all_instances(filters))

def get_instance_by_filters(filters):
    instances = get_instances_by_filters(filters)

    if not instances or len(instances) == 0:
        logger.error("Found no instance for filters %r!" % filters)
        return None

    if len(instances) > 1:
        logger.error("Found more than one instance for filters %r!" % filters)
        return None

    return instances[0]

def get_all_instances():
    return get_instances_by_filters({})

def get_instance_by_tag(tags):
    """ Get a single instance from the EC2 cloud using tags to filter it out.
    Asserts that there is exactly one instance, and returns None when this isn't
    the case. """
    instances = get_instances_by_tags(tags)
    if not instances or len(instances) == 0:
        logger.error("There is no instance matching tags %r" % tags)
        return None

    if len(instances) > 1:
        logger.error("This is confusing .. More than one instance matching %r" %
                     tags)
        return None

    return instances[0]

def get_tags_for_machine(hostname):
    """ Given a hostname, retrieve the tags of that machine in EC2.
    If the machine doesn't exist (or it isn't running), it
    returns None. """

    instance = get_instance_by_filters({'dns-name': hostname})
    if instance is None:
        return None

    return instance.tags

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

def tag_instance(hostname, tags={}):
    instance = get_instance_by_filters({'dns-name': hostname})
    if instance is None:
        return False

    ec2 = boto.connect_ec2()
    return ec2.create_tags([instance.id], tags)
