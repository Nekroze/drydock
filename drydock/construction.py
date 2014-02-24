"""DryDock specification construction functions."""
from os.path import join
import subprocess
from .templates import base_commands, SUPERVISOR_BASE


def prepare():
    for command in base_commands():
        subprocess.call(command)


def construct(specification):
    """Construct the given specification."""
    construct_supervisor(specification)
    construct_nginx(specification)
    construct_containers(specification)


def construct_supervisor(specification):
    """Construct the given specifications supervisor configuration file."""
    filename = join("/etc/supervisor/conf.d/supervisord.conf")

    with open(filename, 'w') as supervisor:
            supervisor.write(SUPERVISOR_BASE + '\n')
            supervisor.write(specification.get_supervisor_config())


def construct_nginx(specification):
    """Construct the given specifications nginx configuration file."""
    filename = join("/etc/nginx/sites-enabled/", specification.domain)

    with open(filename, 'w') as supervisor:
            supervisor.write(specification.get_nginx_config())


def construct_containers(specification):
    """Run the docker commands to construct each container."""
    for name in sorted(specification.containers.keys()):
        container = specification.containers[name]

        subprocess.call(container.get_docker_command())