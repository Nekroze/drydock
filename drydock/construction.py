from __future__ import print_function
__doc__ = """DryDock specification construction functions."""
from os.path import join
import os
from .templates import base_commands, SUPERVISOR_BASE, SUPERVISOR_GROUP


def drydock(http="80", https="443", ssh="2222", name="drydock"):
    print("\nConstructing drydock master container.")
    cmd = "docker run -privileged -name {3} -p {0}:80 -p {1}:443 -p {2}:2222 nekroze/drydock"
    os.system(cmd.format(http, https, ssh, name))


def prepare():
    skydns, skydock, nginx, certificate = base_commands()

    print("\nConstructing skydns container.")
    os.system(skydns)

    print("\nConstructing skydock container.")
    os.system(skydock)

    print("\nConstructing nginx container.")
    os.system(nginx)

    print("\nGenerating SSL/HTTPS certificates for nginx.")
    os.system(certificate)


def deconstruct(specification, supervisor=False):
    """Deconstruct the given specification."""
    if supervisor:
        os.remove("/etc/supervisord.conf")
    os.remove(join("/etc/nginx/sites-enabled/", specification.domain))

    for name in sorted(specification.containers.keys()):
        print("Stopping and Removing " + name)
        os.system("docker stop " + name)
        os.system("docker rm " + name)


def construct(specification, supervisor=False):
    """Construct the given specification."""
    if supervisor:
        construct_supervisor(specification)
    construct_nginx(specification)
    construct_containers(specification)


def construct_supervisor(specification):
    """Construct the given specifications supervisor configuration file."""
    with open("/etc/supervisord.conf", 'w') as supervisor:
            supervisor.write(SUPERVISOR_BASE + '\n')
            supervisor.write(specification.get_supervisor_config())
            supervisor.write(SUPERVISOR_GROUP.format(specification.name,
                ','.join(list(specification.containers.keys()))))


def construct_nginx(specification):
    """Construct the given specifications nginx configuration file."""
    filename = join("/etc/nginx/sites-enabled/", specification.domain)

    with open(filename, 'w') as supervisor:
            supervisor.write(specification.get_nginx_config())


def construct_containers(specification):
    """Run the docker commands to construct each container."""
    for name in sorted(specification.containers.keys()):
        container = specification.containers[name]

        print("\nConstructing " + name)
        os.system(container.get_docker_command())
