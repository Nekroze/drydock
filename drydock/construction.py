import os
import shutil


def ensure_empty_dir(path):
    shutil.rmtree(path)
    os.makedirs(path)


def construct(specification):
    construct_supervisors(specification)
    construct_sites(specification)
    construct_dockerfile(specification)
    construct_buildscript(specification)


def construct_supervisors(specification):
    ensure_empty_dir("supervisor")

    for name, container in specification.containers.items():
        with open(os.path.join("supervisor", "{0}.conf".format(name)), 'w') as supervisor:
            supervisor.write(container.get_supervisor_config())


def construct_sites(specification):
    ensure_empty_dir("site")

    for container in specification.containers.values():
        with open(os.path.join("sites", container.fqdn), 'w') as site:
            site.write(container.get_nginx_config())


def construct_dockerfile(specification):
    with open("Dockerfile", 'w') as dockerfile:
        dockerfile.write('\n'.join(specification.get_dockerfile()))


def construct_buildscript(specification):
    with open("build.sh", 'w') as builder:
        builder.write("#!/bin/sh")
        builder.write(specification.get_docker_commands())