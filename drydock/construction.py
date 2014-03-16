from __future__ import print_function
__doc__ = """DryDock specification construction functions."""
from os.path import join
import os
import time
import docker
from .templates import base_commands, NETWORK
from .report import Report


def master(specification, filename):
    """Construct the given specification in a master container."""
    report = Report()
    print("\nConstructing drydock master container.")
    fqdn = specification.fqdn

    cmd = ' '.join(["mkdir -p /var/lib/{0}/drydock".format(fqdn)])
    report.command("Create specification store", cmd, os.system(cmd))

    cmd = ' '.join(["cp -f", filename,
                    "/var/lib/{0}/drydock/specification.yaml".format(fqdn)])
    report.command("Store specification", cmd, os.system(cmd))

    master = specification.get_docker_command()
    cmds = ["startdocker"]
    cmds.append("drydock prepare")
    cmds.append("drydock pull /drydock/specification.yaml")
    cmd = ' '.join([master, "bash -l -c", '"' + " && ".join(cmds) + '"'])
    report.container(fqdn, cmd, os.system(cmd))

    run = '["bash", "-l", "-c", "{}"]'.format(" && ".join(
        ["drydock construct /drydock/specification.yaml",
         specification.command]))
    cmd = "docker commit --run='{{\"Cmd\": {} }}' {} {}".format(
        run, fqdn, fqdn)
    report.command("Run master supervisor", cmd, os.system(cmd))

    cmd = "docker rm " + fqdn
    report.command("Run master supervisor", cmd, os.system(cmd))

    print(report.render())
    print("Master container run command:")
    print(master)
    report.exit()


def prepare(ssl=False):
    report = Report()
    skydns, skydock, nginx, certificate = base_commands()

    print("\nConstructing skydns container.")
    report.container("skydns", skydns, os.system(skydns))

    print("\nConstructing skydock container.")
    report.container("skydock", skydock, os.system(skydock))

    print("\nConstructing nginx container.")
    report.container("nginx", nginx, os.system(nginx))

    if ssl:
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


def deconstruct(specification):
    """Deconstruct the given specification."""
    report = Report()

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


def construct(specification):
    """Construct the given specification."""
    report = Report()
    construct_nginx(specification, report)
    construct_containers(specification, report)

    cmd = "docker stop nginx && docker start nginx"
    report.command("Restart reverse proxy nginx", cmd, os.system(cmd))

    print(report.render())
    report.exit()


def construct_nginx(specification, report):
    """Construct the given specifications nginx configuration file."""
    filename = join("/etc/nginx/sites-enabled/", specification.domain)

    with open(filename, 'w') as site:
            site.write(specification.get_nginx_config())
    report.path(filename)


def construct_containers(specification, report):
    """Run the docker commands to construct each container."""
    for name in sorted(specification.containers.keys()):
        container = specification.containers[name]

        print("\nConstructing " + name)
        cmd = container.get_docker_command()
        cmd.format(dockerdns=NETWORK["dockerdns"])
        report.container(name, cmd, os.system(cmd))
