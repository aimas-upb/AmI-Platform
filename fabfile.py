import json
import os
import logging
import string
import time

import boto
from fabric.api import run, task, env, local
from fabric.context_managers import settings, cd
from fabric.tasks import execute
from jinja2 import Template

from core.ec2 import (get_tags_for_machine, get_instance_by_tags,
                      get_all_instances, get_instances_by_tags,
                      get_crunch_running, tag_instance)

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

def render_template(template_file, context, target_file=None):
    """ Renders a template to a given destination file, given context vars. """

    with open(template_file, 'rt') as src:
        content = ''.join(src.readlines())
        jinja_template = Template(content)
        output = jinja_template.render(**context)
        if target_file is not None:
            with open(target_file, 'wt') as dest:
                dest.write(output)
        else:
            return output

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
def run_experiment(url='https://raw.github.com/ami-lab/AmI-Platform/master/dumps/diana.txt',
                   name='cloud_experiment',
                   file_name='/tmp/experiment.txt',
                   experiment_profile='default_experiment.json'):

    # Load up which machines are needed from the experiment profile
    machines = json.load(open(experiment_profile, 'rt'))

    # Only open new machines if it's necessary
    opened_instances = get_all_instances()
    if len(opened_instances) == 0:
        # Open exactly the desired number of machines. Sometimes EC2 fails
        # weirdly to open the requested number of machines (don't know why)
        # so I'm putting in a retry mechanism.
        machines_to_open = len(machines)
        machines_opened = 0
        machine_hostnames = []
        while machines_opened < machines_to_open:
            hostnames = execute('open_machines',
                                count=machines_to_open - machines_opened)['<local-only>']
            machine_hostnames.extend(hostnames)
            machines_opened += len(hostnames)
    else:
        hostnames = [instance.public_dns_name for instance in opened_instances]

    # Attach tags to machines. This meta-data is used for provisioning and
    # for the lifecycle management of machines as well.
    for hostname, machine_meta_data in zip(hostnames, machines):
        tag_instance(hostname, machine_meta_data)

    execute('bootstrap_machines')
    execute('provision_machines')
    execute('copy_experiment', url=url, file_name=file_name, name=name)
    execute('play_experiment', name=name)

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
def provision_machines():
    hostnames = [instance.public_dns_name for instance in get_all_instances()]

    # Provision the machines in parallel. The manifest for each machine
    # will be taken from env.hostname_to_manifest, because it's the only sane
    # way I found in fab to do the provisioning in parallel.
    with settings(parallel=True, user='ubuntu',
                  key_filename='/Users/aismail/.ssh/ami-keypair.pem'):
        execute('provision_machine', hosts=hostnames)

    crunch_hostnames = [instance.public_dns_name for instance in
                        get_instances_by_tags({'type': 'crunch'})]

    # For crunch nodes, generate settings_local.py files and services.txt files.
    # Afterwards, run deploy task on each of them.
    with settings(parallel=True, user='ami',
                  key_filename='/Users/aismail/.ssh/ami-keypair.pem'):
        execute('generate_settings_local_file', hosts=crunch_hostnames)
        execute('generate_services_file', hosts=crunch_hostnames)
        execute('deploy_ami_services_on_crunch_node', hosts=crunch_hostnames)

@task
def copy_experiment(url='https://raw.github.com/ami-lab/AmI-Platform/master/dumps/diana.txt',
                    name='cloud_experiment',
                    file_name='/tmp/experiment.txt'):

    # Search among the crunch nodes the one on which ami-recorder is running
    recorder_hostname = get_crunch_running('ami-recorder')
    if recorder_hostname is None:
        print("Something is misconfigured. No crunch node is running the "
              "ami-recorder module, thus we have nowhere to run the experiment")
        return

    with settings(host_string=recorder_hostname):
        with cd('/home/ami/AmI-Platform'):
            # Start and stop the experiment immediately just to create a
            # record in MongoDB in order to fool the experiment system :)
            run('python experiment.py --file %s start %s' %
                (file_name, name))
            run('python experiment.py stop %s' % name)

            # Fetch the dump from the remote location and place it just
            # where the experiment system thinks it recorded it.
            run('wget %s -O %s' % (url, file_name))

@task
def play_experiment(name='cloud_experiment'):

    # Search among the crunch nodes the one on which ami-recorder is running
    recorder_hostname = get_crunch_running('ami-recorder')
    if recorder_hostname is None:
        print("Something is misconfigured. No crunch node is running the "
              "ami-recorder module, thus we have nowhere to run the experiment")
        return

    with settings(host_string=recorder_hostname):
        with cd('/home/ami/AmI-Platform'):
            # This will cause the experiment measurements to be pumped
            # in the kestrel queues, thus triggering the whole processing
            # along the pipeline
            run('python experiment.py play %s' % name)

@task
def deploy_ami_services_on_crunch_node():
    run('cd /home/ami/AmI-Platform; fab deploy:fresh=True')

@task
def deploy(fresh=False):
    with cd('/home/ami/AmI-Platform'):
        # Make sure we have the latest repo version if "fresh" parameter
        # is specified. This will pull the latest version of the code.
        if fresh:
            branch = str(local('git rev-parse --abbrev-ref HEAD'))
            local('git reset --hard HEAD')
            local('git pull origin %s' % branch)
            local('git reset --hard HEAD')
            local('git submodule init')
            local('git submodule update')
            local('cd pybetaface; git pull origin master')

        # Install the latest version of python requirements. For cloud
        # experiments this isn't really necessary, because the hosts are
        # already provisioned by puppet.
        local('sudo pip install -r python_requirements.txt')

        # Compile kinect data acquisition
        local('cd acquisition/kinect; sudo make clean; sudo make')

        # Clean up all pyc's. The safe way to go when you delete a file
        # from the repo.
        local('sudo find . -name "*.pyc" -exec rm -rf {} \;')

        # Clean up the phantom of the old installed services. For this we need
        # the full list of services, in order to know what to look for.
        # This is needed because you might have the following situation:
        # * your host is named xyz
        # * in services.xyz.txt you used to have 2 modules, a and b
        # * in the new version of services.xyz.txt, you only have b
        # * this would mean that the only way out without having a full list
        #   of services is to run the clean-up routine after fetching the new
        #   code, but this is unacceptable for several reasons:
        #   ** first, because administrative code should always be ran on the
        #      latest version from master (e.g. fabfile)
        #   ** second, because services.xyz.txt might be dirty and totally
        #      screwed up anyway (working on a dirty tree)
        with open('services.txt', 'rt') as f:
            all_services = filter(lambda x: len(x) > 0, [l.strip() for l in f.readlines()])
            for service in all_services:
                # For each service, we need to clean up 2 things:
                # - upstart script - transforms the python script into a
                #   system-level service
                # - monit script - makes sure that the script is running
                #   continuously
                upstart_script = '/etc/init/%s.conf' % service
                if os.path.exists(upstart_script):
                    print('Removing old upstart script for service %s' % service)
                    local('sudo rm %s' % upstart_script)

                monit_script = '/etc/monit/conf.d/%s' % service
                if os.path.exists(monit_script):
                    print('Removing old monit script for service %s' % service)
                    local('sudo rm %s' % monit_script)

        # Try to get a host-specific services file in order to know what
        # services to install. If none is available, install all services
        # by default
        host_services_file = 'services.%s.txt' % str(local('hostname -s', capture=True))
        services_file = host_services_file if os.path.exists(host_services_file) else 'services.txt'

        with open(services_file, 'rt') as f:
            services = filter(lambda x: len(x) > 0, [l.strip() for l in f.readlines()])
            for service in services:
                # For each service in the services file, we copy the upstart
                # and monit scripts to the correct locations, and restart
                # the service. Restarting the service is needed because the code
                # might have been modified in the latest revision of the repo.
                # Copying the config files from scratch is also needed because
                # they might have been modified as well.
                print("====================================================")
                print("      Redeploying service %s                        " % service)
                print("====================================================")
                print("")
                print("Copying new upstart script for service %s" % service)
                local('sudo cp scripts/upstart/%s.conf /etc/init' % service)
                print("Copying new monit script for service %s" % service)
                local('sudo cp scripts/monit/%s /etc/monit/conf.d' % service)
                print("Restarting service %s" % service)
                local('sudo service %s restart' % service)

@task
def generate_services_file():
    """ Given a crunch node, generate a settings_local.py file which
    contains the list of services that should run on this machine. """

    tags = get_tags_for_machine(env.host_string)
    if not 'modules' in tags:
        print("No modules are specified as EC2 tags for hostname %s" %
              env.host_string)
        return

    modules = tags['modules'].split(',')
    file_path = ('/home/ami/AmI-Platform/services.%s.txt' %
                 str(run('hostname -s')))
    run('echo "" > %s' % file_path)
    for module in modules:
        run('echo "%s" >> %s' % (module, file_path))

@task
def generate_settings_local_file():
    """ Given a crunch node, generate a settings.py file pointing the modules
    running on it to the correct resources (redis/kestrel/mongodb/etc). """

    mongo = get_instance_by_tags({'Name': 'measurements'})
    if not mongo:
        print("Could not find measurements DB in the cloud!")
        return

    redis = get_instance_by_tags({'Name': 'sessions'})
    if not redis:
        print("Could not find sessions DB in the cloud!")
        return

    kestrel = get_instance_by_tags({'Name': 'queues'})
    if not kestrel:
        print("Could not find queues machine in the cloud!")
        return

    # Render the settings_local.py file template to a string.
    context = {
        'kestrel_server': kestrel,
        'kestrel_port': 22133,
        'mongo_server': mongo,
        'mongo_port': 27017,
        'redis_server': redis,
        'redis_port': 6379,
    }
    content = render_template('admin/templates/settings.py', context).split('\n')

    # Afterwards, string is written line by line using echo to the remote
    # host.
    file_path = '/home/ami/AmI-Platform/core/settings_local.py'
    run('echo "" > %s' % file_path)
    for line in content:
        run('echo "%s" > %s' % (line, file_path))

@task
def bootstrap_machines():
    hostnames = [instance.public_dns_name for instance in get_all_instances()]

    # Provision the machines in parallel. The manifest for each machine
    # will be taken from env.hostname_to_manifest, because it's the only sane
    # way I found in fab to do the provisioning in parallel.
    with settings(parallel=True, user='ubuntu',
                  key_filename='/Users/aismail/.ssh/ami-keypair.pem'):
        execute('bootstrap_machine', hosts=hostnames)

@task
def bootstrap_machine():
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

@task
def provision_machine(manifest='crunch_01.pp'):
    # Retrieve EC2 tags for this machine, and see if there is a manifest tag
    # among them. If yes, that one has priority over what gets specified as
    # a parameter to this function.
    tags = get_tags_for_machine(env.host_string)
    if 'manifest' in tags:
        manifest = tags['manifest']

    # Run the actual manifest for provisioning this node from the repo
    run("sudo puppet apply /home/ami/AmI-Platform/provisioning/nodes/%s" % manifest)
