"""DryDock cluster specification."""


class Container(object):
    """A docker container specification."""
    def __init__(self, name, base="ubuntu", exposed_ports=None,
                 external=False, http_port=0, https_port=0, commands=None):
        self.name = name
        self.base = base
        self.exposed_ports = {}
        self.exposed_ports.update(exposed_ports)
        self.http_port = 0
        self.https_port = 0
        self.external = external
        self.commands = [] if not commands else commands


class MetaContainer(Container):
    """A container that stores containers."""
    def __init__(self, name, domain, subcontainers, commands=None, base="nekroze/drydock"):
        super(MetaContainer, self).__init__(name=name, base=base, commands=commands)
        self.domain = domain
        self.containers = {}
        self.reverse_proxies = {}

        for sub in subcontainers:
            self.add_container(Container(**sub))

    def add_container(self, container):
        self.containers[container.name] = container
        self.exposed_ports.update(container.exposed_ports)

        fqdn = container.name + '.' + self.domain
        self.reverse_proxies[fqdn] = {
            "external": container.external,
            "http": container.http_port,
            "https": container.https_port
        }