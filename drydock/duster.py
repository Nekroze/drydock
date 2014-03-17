"""DryDock cluster specification."""
from .templates import render_nginx_config, TEMPLATES
from six.moves.urllib.request import urlopen
import yaml


class Container(object):
    """A docker container specification."""
    def __init__(self, name, base="ubuntu", exposed_ports=None, external=True,
                 http_port="80", https_port="443", domain="", volumes=None,
                 envs=None, command=None, data=False):
        self.name = name
        self.domain = ""
        self.fqdn = ""
        self.base = base
        self.envs = envs if envs else {}
        self.data = data
        self.exposed_ports = {}
        self.command = command
        self.http = False
        self.https = False
        if exposed_ports:
            self.exposed_ports.update(exposed_ports)
        self.http_port = http_port
        self.https_port = https_port
        self.external = external
        self.volumes = volumes if volumes else []
        self.set_domain(domain)

    def set_domain(self, domain):
        """Set fqdn and domain."""
        self.domain = domain
        if self.name == "root":
            self.fqdn = self.domain
        else:
            self.fqdn = self.name + '.' + self.domain
        self.skyfqdn = '.'.join([self.name, self.base.split('/')[-1],
                                 "containers", "drydock"])

    def get_portmaps(self):
        """Get docker command port maps."""
        output = []
        for external in sorted(self.exposed_ports.keys()):
            output.append("-p {0}:{1}".format(external,
                                           self.exposed_ports[external]))
        return output

    def get_volumemaps(self):
        """Return docker command volume maps."""
        output = []
        for path in self.volumes:
            output.append("-v /var/lib/{0}/{1}{2}:{2}".format(
                self.domain, self.name, path))
        return output

    def get_envs(self):
        """Return docker environment variable arguments."""
        output = []
        for name, value in self.envs.items():
            output.append("-e \"{0}={1}\"".format(name, value))
        return output

    def get_docker_command(self):
        """Return the docker command required to create this container."""
        cmd = ["docker run -d --dns {dockerdns}"]
        cmd.append("--name " + self.name)
        cmd.append("-h " + self.fqdn)
        cmd.extend(self.get_portmaps())
        if self.data:
            cmd.append("-v /var/lib/{}/drydock/data:/mnt/data".format(
                self.domain))
        cmd.append("-v /etc/timezone:/etc/timezone:ro")
        cmd.extend(self.get_volumemaps())
        cmd.extend(self.get_envs())
        cmd.append(self.base)
        if self.command:
            cmd.append(self.command)
        return ' '.join(cmd)

    def get_nginx_config(self):
        """Get a rendered nginx configuration file for this container."""
        return render_nginx_config(self)


class MetaContainer(Container):
    """A container that stores containers."""
    def __init__(self, name, domain, subcontainers, base="nekroze/drydock", *args,  **kwargs):
        super(MetaContainer, self).__init__(*args, name=name, base=base,
                                            domain=domain, **kwargs)
        if not self.command:
            self.command = \
                "startdocker && drydock supervise /drydock/specification.yaml"
        self.containers = {}
        self.reverse_proxies = {}
        self.fqdn = domain
        self.exposed_ports[self.http_port] = "80"
        self.exposed_ports[self.https_port] = "443"

        for sub in subcontainers:
            if "specification" in sub:
                sub = self.grab_specification(sub["specification"], sub)
            container = Container(**sub)
            container.http = "http_port" in sub
            container.https = "https_port" in sub
            self.add_container(container)

    def grab_specification(self, link, base):
        """Create a container specification based off of a web link."""
        spec = yaml.load(urlopen(link).read()) if link else {}
        spec.update(base)
        del spec["specification"]
        return spec

    def set_domain(self, domain):
        """Set fqdn and domain to the same value."""
        self.domain = domain
        self.fqdn = domain

    def add_container(self, container):
        """Add the given container object to this meta container."""
        if not container.domain and self.domain:
            container.set_domain(self.domain)

        self.containers[container.name] = container
        self.exposed_ports.update(container.exposed_ports)

        fqdn = container.name + '.' + self.domain
        self.reverse_proxies[fqdn] = {
            "skyfqdn": container.skyfqdn,
            "external": container.external,
            "http": container.http_port,
            "https": container.https_port
        }

    def get_nginx_config(self):
        """Get a rendered nginx configuration file for all containers."""
        #output = [TEMPLATES["NGINX"]["HEADER"]]
        output = []
        for name in sorted(self.containers.keys()):
            container = self.containers[name]
            output.append(container.get_nginx_config())
        return '\n'.join(output)

    def get_volumemaps(self):
        """Return docker command volume maps."""
        output = []
        for path in self.volumes:
            output.append("-v /var/lib/{0}{1}:{1}".format(self.name, path))
        return output

    def get_docker_command(self):
        """
        Return the docker command required to create specification in
        a master container.
        """
        cmd = ["docker run --privileged"]
        cmd.append("--name {}".format(self.name))
        cmd.append("-h " + self.fqdn)
        cmd.extend(self.get_portmaps())
        ngx = "-v /var/lib/{}/nginx/sites-enabled:/etc/nginx/sites-enabled"
        cmd.append(ngx.format(self.fqdn))
        ngx = "-v /var/lib/{}/nginx/ssl:/etc/nginx/ssl:ro"
        cmd.append(ngx.format(self.fqdn))
        cmd.append("-v /etc/timezone:/etc/timezone:ro")
        cmd.append("-v /var/lib/{0}/docker:/var/lib/docker".format(
            self.name))
        cmd.append("-v /var/lib/{0}:/var/lib/{1}".format(
            self.name, self.fqdn))
        cmd.append("-v /var/lib/{0}/drydock/data:/var/lib/{0}/drydock/data".format(
            self.name))
        cmd.append("-v /var/lib/{0}/drydock:/drydock:ro".format(self.fqdn))
        cmd.extend(self.get_volumemaps())
        cmd.append(self.base)
        return ' '.join(cmd)