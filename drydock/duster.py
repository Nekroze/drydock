"""DryDock cluster specification."""


class Container(object):
    """A docker container specification."""
    def __init__(self, name, base="ubuntu", exposed_ports=None,
                 external=False, http_port=0, https_port=0):
        self.name = name
        self.base = base
        self.exposed_ports = {}
        self.exposed_ports.update(exposed_ports)
        self.http_port = 0
        self.https_port = 0
        self.external = external
        self.commands = []

    def get_container_commands(self):
        self.commands = []
        run = 'docker run -d'.split(' ')

        run.append("--name {0}".format(self.name))

        for external, internal in self.exposed_ports.items():
            run.append("-p {0}:{1}".format(external, internal))

        run.append(self.base)
        self.commands.append("RUN " + ' '.join(run))
        self.commands.append("ADD {0}.conf /etc/supervisor/conf.d/{0}.conf".format(self.name))

    def write_supervisor_config(self):
        with open("{0}.conf".format(self.name), 'w') as config:
            config.write("""[program:{0}]
command=docker start {0}
autostart=true
autorestart=true""".format(self.name))


class MetaContainer(Container):
    """A container that stores containers."""
    def __init__(self, name, domain, subcontainers, base="nekroze/drydock"):
        super(MetaContainer, self).__init__(name=name, base=base)
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
            "skyfqdn": '.'.join([container.name, container.base.split('/')[-1], "containers", "drydock"]),
            "external": container.external,
            "http": container.http_port,
            "https": container.https_port
        }