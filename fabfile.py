import os
import logging
import string
import time

import boto
from fabric.api import run, task
from fabric.context_managers import settings
from fabric.tasks import execute
from jinja2 import Template

logger = logging.getLogger(__name__)

def get_services():
    """ Returns the set of already defined services. """
    with open("services.txt") as f:
        services = [line[:-1] for line in f.readlines()]
        return filter(lambda x: len(x) > 0, services)

def service_already_exists(name):
    """ Check if a service with the given name already exists. """
    return name in set(get_services())

def default_file_name(name):
    """ Given a service name, provide a good default for a file name. """

    if name.startswith('ami-'):
        return 'pipeline/' + name[4:] + '.py'
    else:
        return 'pipeline/' + name + '.py'

def default_queue_name(name):
    """ Given a service name, provide a good default for a queue name. """

    if name.startswith('ami-'):
        return name[4:]
    else:
        return name

def default_class_name(name):
    """ Given a service name, provide a good default for a class name. """
    if name.startswith('ami-'):
        dashed_name = name[4:]
    else:
        dashed_name = name
    return string.capwords(dashed_name.replace('-', ' ')).replace(' ', '')

def render_template(template_file, context, target_file):
    """ Renders a template to a given destination file, given context vars. """

    with open(template_file, 'rt') as src:
        content = ''.join(src.readlines())
        jinja_template = Template(content)
        output = jinja_template.render(**context)
        with open(target_file, 'wt') as dest:
            dest.write(output)

@task
def new_service(name, file = None, queue = None, class_name = None):
    """ Installs a new service with the given name. """

    if service_already_exists(name):
        print "A service with the name %s already exists." % name
        return

    file = file or default_file_name(name)
    queue = queue or default_queue_name(name)
    class_name = class_name or default_class_name(name)

    context = {
        'service_class_name': class_name,
        'service_queue': queue,
        'service_name': name,
        'service_file': file,
        'service_description': '%s service for AmI Lab' % class_name
    }

    # Generate dumb code file
    print "Generating code file %s" % file
    render_template('admin/templates/service-code.py',
                    context,
                    file)

    # Generate monit script - make sure that the service is never down
    print "Generating monit script scripts/monit/%s" % name
    render_template('admin/templates/service-monit',
                    context,
                    'scripts/monit/%s' % name)

    # Generate upstart script - make it a system service
    print "Generating upstart script scripts/upstart/%s.conf" % name
    render_template('admin/templates/service-upstart',
                    context,
                    'scripts/upstart/%s.conf' % name)

    # Generate shell script that runs it + make it executable
    print "Generating shell that runs the service scripts/shell/%s.sh" % name
    render_template('admin/templates/service-shell',
                    context,
                    'scripts/shell/%s.sh' % name)
    os.chmod('scripts/shell/%s.sh' % name, 0755)

    # Append service name to services.txt
    services = get_services()
    services.append(name)
    services.append('')
    with open('services.txt', 'wt') as f:
        f.write('\n'.join(services))

@task
def open_and_provision_machine(machine_type='m1.small',
                               manifest='crunch_01.pp',
                               ami_id='ami-d0f89fb9'):
    """
        Opens up an EC2 machine and provisions it with the given puppet
        manifest. You can optionally specify an AMI id, or otherwise
        use the AMI provided by Canonical with Ubuntu 12.04 LTS.
    """
    ec2 = boto.connect_ec2()
    reservation = ec2.run_instances(image_id=ami_id, security_group_ids=['sg-82df60e9'], key_name='ami-keypair')
    print("Created reservation for 1 instance: %r" % reservation)

    instance = reservation.instances[0]
    status = instance.update()
    while status == 'pending':
        print("Waiting for another 10 seconds for machine to show up..")
        time.sleep(10)
        status = instance.update()

    if status != 'running':
        print("Machine didn't start OK, status = %s" % status)
        return

    print("Giving the SSH daemon the opportunity to start up and stuff..")
    time.sleep(30)

    with settings(user='ubuntu', key_filename='/Users/aismail/.ssh/ami-keypair.pem'):
        execute('provision_machine', host=instance.public_dns_name, manifest=manifest)

    return instance.public_dns_name

@task
def provision_machine(manifest='crunch_01.pp'):
    # http://docs.puppetlabs.com/guides/puppetlabs_package_repositories.html#for-debian-and-ubuntu
    run('cd /tmp; wget http://apt.puppetlabs.com/puppetlabs-release-precise.deb')
    run('sudo dpkg -i /tmp/puppetlabs-release-precise.deb')
    run('sudo apt-get -y update')

    # we are running masterless puppet to simplifiy automatic setup and teardown
    run('sudo apt-get -y install puppet')
    run('sudo puppet module install -f puppetlabs/apt')
    run('sudo puppet module install -f puppetlabs/gcc')
    run('sudo puppet module install -f puppetlabs/mongodb')
    run('sudo puppet module install -f puppetlabs/stdlib')
    run('sudo puppet module install -f puppetlabs/vcsrepo')
    run('sudo puppet module install -f maestrodev/ssh_keygen')
    run('sudo puppet module install -f maestrodev/wget')
    run('sudo puppet module install -f thomasvandoren/redis')

    # Fetch puppet config file - most notable change is modulepath which points
    # to local repo dir as well.
    run('cd /etc/puppet; sudo rm puppet.conf; sudo wget https://raw.github.com/ami-lab/AmI-Platform/master/provisioning/puppet.conf')

    # Fetch & apply bootstrap manifest - fetch the repo with the rest of the
    # manifests in the correct dir with the correct permissions.
    run('cd /tmp; wget https://raw.github.com/ami-lab/AmI-Platform/master/provisioning/bootstrap.pp')
    run('sudo puppet apply /tmp/bootstrap.pp')

    # Run the actual manifest for provisioning this node from the repo
    run("sudo puppet apply /home/ami/AmI-Platform/provisioning/nodes/%s" % manifest)
