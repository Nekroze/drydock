"""DryDock specification construction functions."""
import os
import shutil


def ensure_empty_dir(path):
    """Remove the given directory and recreate it."""
    shutil.rmtree(path)
    os.makedirs(path)


def construct(specification, path):
    """Construct the given specification into files."""
    construct_supervisors(specification, path)
    construct_sites(specification, path)
    construct_dockerfile(specification, path)
    construct_buildscript(specification, path)


def construct_supervisors(specification, path):
    """Construct the given specifications supervisor configuration files."""
    path = os.path.join(path, "supervisor")
    ensure_empty_dir(path)

    for name, container in specification.containers.items():
        with open(os.path.join(path, "{0}.conf".format(name)), 'w')\
                as supervisor:
            supervisor.write(container.get_supervisor_config())


def construct_sites(specification, path):
    """Construct the given specifications nginx configuration files."""
    path = os.path.join(path, "site")
    ensure_empty_dir(path)

    for container in specification.containers.values():
        with open(os.path.join(path, container.fqdn), 'w') as site:
            site.write(container.get_nginx_config())


def construct_dockerfile(specification, path):
    """Construct the given specifications Dockerfile."""
    with open(os.path.join(path, "Dockerfile"), 'w') as dockerfile:
        dockerfile.write('\n'.join(specification.get_dockerfile()))


def construct_buildscript(specification, path):
    """Construct the given specifications build script."""
    with open(os.path.join(path, "build.sh"), 'w') as builder:
        builder.write("#!/bin/sh")
        builder.write(specification.get_docker_commands())
