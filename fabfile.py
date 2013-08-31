import os
import logging
import string
import time

import boto
from fabric.api import run, task, env
from fabric.context_managers import settings
from fabric.operations import put
from fabric.tasks import execute
from jinja2 import Template

env.connection_attempts = 5

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
def run_experiment():

    # Mapping from nodes to installed services on them.
    crunch_nodes = {
        'crunch_01': {
            'modules': ['ami-router', 'ami-mongo-writer',
                        'ami-room-position', 'ami-dashboard']
        },

        'crunch_02': {
            'modules': ['ami-head-crop']
        },

        'crunch_03': {
            'modules': ['ami-face-recognition']
        },

        'crunch_04': {
            'modules': ['ami-upgrade_face_samples', 'ami-room', 'ami-ip-power']
        },

        'crunch_05': {
            'modules': ['ami-recorder']
        }
    }

    # Open exactly the desired number of machines. Sometimes EC2 fails
    # weirdly to open the requested number of machines (don't know why)
    # so I'm putting in a retry mechanism.
    machines_to_open = len(crunch_nodes) + 3
    machines_opened = 0
    machine_hostnames = []
    while machines_opened < machines_to_open:
        hostnames = execute('open_machines',
                            count=machines_to_open - machines_opened)['<local-only>']
        machine_hostnames.extend(hostnames)
        machines_opened += len(hostnames)

    # Map the freshly obtained hostnames to manifests
    manifests = {}
    manifests[hostnames[0]] = 'mongo.pp'
    manifests[hostnames[1]] = 'redis.pp'
    manifests[hostnames[2]] = 'kestrel.pp'
    i = 1
    for crunch_hostname in hostnames[3:]:
        manifests[crunch_hostname] = 'crunch_01.pp'
        crunch_nodes['crunch_0%d' % i]['hostname'] = crunch_hostname
        i += 1
    env.hostname_to_manifest = manifests

    # Provision the machines in parallel. The manifest for each machine
    # will be taken from env.hostname_to_manifest, because it's the only sane
    # way I found in fab to do the provisioning in parallel.
    with settings(parallel=True, user='ubuntu',
                  key_filename='/Users/aismail/.ssh/ami-keypair.pem'):
        execute('provision_machine', hosts=hostnames)

    # Generate settings_local.py based on the hostnames of the opened machines
    # This is needed in order to wire up the machines with knowledge of the
    # MongoDB / Redis / Kestrel server so that they connect to it correctly.
    # Since we're generating the file in the /tmp dir, make sure we clean up
    # a potentially existing old file before we use it.
    context = {
        'kestrel_server': hostnames[2],
        'kestrel_port': 22133,
        'mongo_server': hostnames[0],
        'mongo_port': 27017,
        'redis_server': hostnames[1],
        'redis_port': 6379,
    }
    try:
        os.remove('/tmp/settings.py.generated')
    except:
        pass

    render_template('admin/templates/settings.py',
                    context,
                    '/tmp/settings.py.generated')

    # Copy the settings.py to each machine, and generate services.txt
    # for each one. The name of the services file is based on the `hostname -s`
    # command (see deploy.sh command for more details), and its content
    # will enable deploy.sh to install the AmI services correctly as system
    # services managed by upstart & monit (these guys are installed prior to
    # this step via puppet).
    for crunch_node in crunch_nodes.iterkeys():
        hostname = crunch_nodes[crunch_node]['hostname']
        with settings(host_string=hostname, user='ami',
                      key_filename='/Users/aismail/.ssh/ami-keypair.pem'):

            # Copy the generated settings file to core/settings_local.py
            # If you overwrite core/settings.py, that one gets overwritten
            # at ./deploy.sh --fresh
            put('/tmp/settings.py.generated', '/home/ami/AmI-Platform/core/settings_local.py')

            # Get local hostname and generate a services.hostname.txt file
            local_hostname = str(run('hostname -s'))
            services_filename = '/tmp/services.%s.txt' % local_hostname

            try:
                os.remove(services_filename)
            except:
                pass

            with open(services_filename, 'wt') as f:
                f.write('\n'.join(crunch_nodes[crunch_node]['modules'] + []))


            # Copy the services file remotely and execute a deploy.sh.
            # That will cause the ami services designated for this node to
            # be installed.
            put(services_filename, '/home/ami/AmI-Platform')

    # Install the AmI services on each machine in parallel. The reason is that
    # this might require some compilation from sources, and that tends to be
    # slow.
    with settings(parallel=True, user='ami',
                  key_filename='/Users/aismail/.ssh/ami-keypair.pem'):
        execute('deploy_ami_services_on_crunch_node', hosts=hostnames)


    # copy dump where experiment.py should be run
    # create experiment record in mongo
    # profit :)

    import pprint
    pprint.pprint(env.hostname_to_manifest)
    pprint.pprint(crunch_nodes)

@task
def open_machines(machine_type='m1.small',
                  manifest='crunch_01.pp',
                  ami_id='ami-d0f89fb9',
                  count=1):

    ec2 = boto.connect_ec2()
    reservation = ec2.run_instances(image_id=ami_id,
                                    min_count=count,
                                    max_count=count,
                                    security_group_ids=['sg-82df60e9'],
                                    key_name='ami-keypair')
    print("Created reservation for %d instances: %r" % (count, reservation))

    statuses = [instance.update() for instance in reservation.instances]
    while any(status == 'pending' for status in statuses):
        print("Waiting for 10 seconds for machine(s) to show up..")
        time.sleep(10)
        statuses = [instance.update() for instance in reservation.instances]

    failed_machines = 0
    public_hostnames = []
    for idx, status in enumerate(statuses):
        if status != 'running':
            failed_machines += 1
        else:
            public_hostnames.append(reservation.instances[idx].public_dns_name)

    if failed_machines > 0:
        print("%d machines failed to start!" % failed_machines)
    else:
        print("All %d machines were started correctly." % count)

    time.sleep(10)

    return public_hostnames

@task
def deploy_ami_services_on_crunch_node():
    run('cd /home/ami/AmI-Platform; ./deploy.sh --fresh')

@task
def provision_machine(manifest='crunch_01.pp'):

    # Give priority to what is found in env.hostname_to_manifest if such
    # an entry is found.
    host = env.host_string
    if hasattr(env, 'hostname_to_manifest') and host in env.hostname_to_manifest:
        manifest = env.hostname_to_manifest[host]

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
