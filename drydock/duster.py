"""DryDock cluster specification."""
from . import templates


class Container(object):
    """A docker container specification."""
    def __init__(self, name, base="ubuntu", exposed_ports=None, external=True,
                 http_port=0, https_port=0, domain="", volumes=None):
        self.name = name
        self.domain = ""
        self.fqdn = ""
        self.set_domain(domain)
        self.base = base
        self.exposed_ports = {}
        if exposed_ports:
            self.exposed_ports.update(exposed_ports)
        self.http_port = http_port
        self.https_port = https_port
        self.external = external
        self.volumes = volumes if volumes else []
        self.skyfqdn = '.'.join([self.name, self.base.split('/')[-1],
                                 "containers", "drydock"])

    def set_domain(self, domain):
        """Set fqdn and domain."""
        self.domain = domain
        if self.name == "root":
            self.fqdn = self.domain
        else:
            self.fqdn = self.name + '.' + self.domain

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
            output.append("-v /var/lib/{0}{1}:{1}".format(self.name, path))
        return output

    def get_docker_command(self):
        """Return the docker command required to create this container."""
        cmd = ["docker run -d -dns 172.17.42.1"]
        cmd.append("-name " + self.name)
        cmd.extend(self.get_portmaps())
        cmd.extend(self.get_volumemaps())
        cmd.append(self.base)
        return ' '.join(cmd)

    def get_supervisor_config(self):
        """Get a rendered supervisor configuration file for thiscontainer."""
        return templates.SUPERVISOR_CONTAINER.format(self.name)

    def get_nginx_config(self):
        """Get a rendered nginx configuration file for this container."""
        return templates.render_nginx_config(self)


class MetaContainer(Container):
    """A container that stores containers."""
    def __init__(self, name, domain, subcontainers, base="nekroze/drydock",
                 *args, **kwargs):
        super(MetaContainer, self).__init__(*args, name=name, base=base,
                                            domain=domain, **kwargs)
        self.containers = {}
        self.reverse_proxies = {}
        self.fqdn = domain

        for sub in subcontainers:
            self.add_container(Container(**sub))

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
        output = []
        for name in sorted(self.containers.keys()):
            container = self.containers[name]
            output.append(container.get_nginx_config())
        return '\n'.join(output)

    def get_supervisor_config(self):
        """Get a rendered supervisor configuration file for all containers."""
        output = []
        for name in sorted(self.containers.keys()):
            container = self.containers[name]
            output.append(container.get_supervisor_config())
        return '\n'.join(output)