from __future__ import print_function
__doc__ = """DryDock specification construction functions."""
from os.path import join
import os
import time
import docker
from .templates import base_commands, SUPERVISOR_BASE, SUPERVISOR_GROUP
from .report import Report


def master(http="80", https="443", ssh="2222", name="drydock"):
    report = Report()
    print("\nConstructing drydock master container.")
    cmd = "docker run -privileged -name {3} -p {0}:80 -p {1}:443 -p {2}:2222 nekroze/drydock"
    cmd = cmd.format(http, https, ssh, name)
    report.container(name, cmd, os.system(cmd))

    print(report.render())
    report.exit()


def prepare():
    report = Report()
    skydns, skydock, nginx, certificate = base_commands()

    print("\nConstructing skydns container.")
    report.container("skydns", skydns, os.system(skydns))

    print("\nConstructing skydock container.")
    report.container("skydock", skydock, os.system(skydock))

    print("\nConstructing nginx container.")
    report.container("nginx", nginx, os.system(nginx))

    print("\nGenerating SSL/HTTPS certificates for nginx.")
    report.command("Generate SSL Certificates", certificate,
                   os.system(certificate))

    print(report.render())
    report.exit()


def pull(specification):
    """Pull all images for the given specification."""
    report = Report()

    cmd = "docker pull crosbymichael/skydns"
    report.command("Pull image skydns", cmd, os.system(cmd))
    cmd = "docker pull crosbymichael/skydock"
    report.command("Pull image skydns", cmd, os.system(cmd))
    cmd = "docker pull dockerfile/nginx"
    report.command("Pull image nginx", cmd, os.system(cmd))

    for name in sorted(specification.containers.keys()):
        base = specification.containers[name].base
        cmd = "docker pull " + base
        report.command("Pull image " + base, cmd, os.system(cmd))

    print(report.render())
    report.exit()


def start(specification):
    """Start all containers defined in the given specification."""
    report = Report()

    cmd = "docker start skydns"
    report.command("Start container skydns", cmd, os.system(cmd))
    cmd = "docker start skydock"
    report.command("Start container skydns", cmd, os.system(cmd))

    for name in sorted(specification.containers.keys()):
        cmd = "docker start " + name
        report.command("Start container " + name, cmd, os.system(cmd))

    cmd = "docker start nginx"
    report.command("Start container nginx", cmd, os.system(cmd))

    print(report.render())
    report.exit()


def supervise(specification):
    """Supervise all containers defined in the given specification."""
    containers = ["skydns", "skydock"]
    containers.extend(sorted(specification.containers.keys()))
    containers.append("nginx")

    dock = docker.Client(base_url='unix://var/run/docker.sock')
    os.system("docker stop nginx && docker rm nginx")
    os.system(base_commands()[2])

    while True:
        ps = {cont["Names"][0][1:]: cont["Status"]
              for cont in dock.containers(all=True)}
        for tag in containers:
            if "Exit" in ps[tag]:  # check for exit status
                print("Container has stopped: {} Code: {}".format(
                    tag, ps[tag][5:]))
                dock.start(tag)
        time.sleep(30)


def stop(specification):
    """Stop all containers defined in the given specification."""
    report = Report()

    cmd = "docker stop skydns"
    report.command("Stop container skydns", cmd, os.system(cmd))
    cmd = "docker stop skydock"
    report.command("Stop container skydns", cmd, os.system(cmd))
    cmd = "docker restart nginx"
    report.command("Stop container nginx", cmd, os.system(cmd))

    for name in sorted(specification.containers.keys()):
        cmd = "docker stop " + name
        report.command("Stop container " + name, cmd, os.system(cmd))

    print(report.render())
    report.exit()


def deconstruct(specification, supervisor=False):
    """Deconstruct the given specification."""
    report = Report()

    if supervisor:
        path = "/etc/supervisord.conf"
        if os.path.exists(path):
            os.remove(path)
        report.path(path)

    path = join("/etc/nginx/sites-enabled/", specification.domain)
    if os.path.exists(path):
        os.remove(path)
    report.path(path)

    for name in sorted(specification.containers.keys()):
        print("Stopping and Removing " + name)
        cmd = "docker stop " + name
        report.command("Stop container " + name, cmd, os.system(cmd))

        cmd = "docker rm " + name
        report.container(name, cmd, os.system(cmd))

    print(report.render(True))
    report.exit()


def construct(specification, supervisor=False):
    """Construct the given specification."""
    report = Report()

    if supervisor:
        construct_supervisor(specification, report)
    construct_nginx(specification, report)
    construct_containers(specification, report)

    cmd = "docker stop nginx && docker start nginx"
    report.command("Restart reverse proxy nginx", cmd, os.system(cmd))

    print(report.render())
    report.exit()


def construct_supervisor(specification, report):
    """Construct the given specifications supervisor configuration file."""
    with open("/etc/supervisord.conf", 'w') as supervisor:
            supervisor.write(SUPERVISOR_BASE + '\n')
            supervisor.write(specification.get_supervisor_config())
            supervisor.write(SUPERVISOR_GROUP.format(specification.name,
                ','.join(list(specification.containers.keys()))))
    report.path("/etc/supervisord.conf")


def construct_nginx(specification, report):
    """Construct the given specifications nginx configuration file."""
    filename = join("/etc/nginx/sites-enabled/", specification.domain)

    with open(filename, 'w') as supervisor:
            supervisor.write(specification.get_nginx_config())
    report.path(filename)


def construct_containers(specification, report):
    """Run the docker commands to construct each container."""
    for name in sorted(specification.containers.keys()):
        container = specification.containers[name]

        print("\nConstructing " + name)
        cmd = container.get_docker_command()
        report.container(name, cmd, os.system(cmd))
