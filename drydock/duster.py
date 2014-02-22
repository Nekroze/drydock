"""DryDock cluster specification."""
from . import templates


class Container(object):
    """A docker container specification."""
    def __init__(self, name, base="ubuntu", exposed_ports=None,
                 external=False, http_port=0, https_port=0, domain=""):
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
        self.commands = []
        self.skyfqdn = '.'.join([self.name, self.base.split('/')[-1], "containers", "drydock"])

    def set_domain(self, domain):
        """Set fqdn and domain."""
        self.domain = domain
        if self.name == "root":
            self.fqdn = self.domain
        else:
            self.fqdn = self.name + '.' + self.domain

    def get_container_commands(self):
        """Return a list of commands required to construct and use this container specification."""
        commands = []
        run = 'docker run -d'.split(' ')

        run.append("--name {0}".format(self.name))

        for external, internal in self.exposed_ports.items():
            run.append("-p {0}:{1}".format(external, internal))

        run.append(self.base)
        commands.append("RUN " + ' '.join(run))
        commands.append("ADD supervisor/{0}.conf /etc/supervisor/conf.d/{0}.conf".format(self.name))

        if self.http_port or self.https_port:
            commands.append("ADD sites/{0} /etc/nginx/sites-enabled/{0}".format(self.fqdn))
        return '\n'.join(commands.extend(self.commands))

    def get_supervisor_config(self):
        """Write this containers supervisor configuration file to `./supervisor/{Container.name}.conf`"""
        return """[program:{0}]
command=docker start {0}
autostart=true
autorestart=true""".format(self.name)

    def get_nginx_config(self):
        """Write this containers nginx site configuration to `./sites/{Container.fqdn}`"""
        return templates.render_nginx_config(self)


class MetaContainer(Container):
    """A container that stores containers."""
    def __init__(self, name, domain, subcontainers, base="nekroze/drydock", *args, **kwargs):
        super(MetaContainer, self).__init__(*args, name=name, base=base, domain=domain, **kwargs)
        self.containers = {}
        self.reverse_proxies = {}
        self.fqdn = domain

        for sub in subcontainers:
            self.add_container(Container(**sub))

    def set_domain(self, domain):
        """Set fqdn and domain."""
        self.domain = domain
        self.fqdn = domain

    def add_container(self, container):
        """Add the given container object to this meta container."""
        if self.domain:
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

    def get_portmaps(self):
        template = "-p {0}:{1}"
        portmaps = [template.format("80", "80"), template.format("443", "443")]

        for container in self.containers:
            for port in container.exposed_ports.keys():

                portmap = template.format(port, port)
                if portmap not in portmaps:
                    portmaps.append(portmap)

        return ' '.join(portmaps)

    def get_docker_commands(self):
        commands = ["docker build -t {name}-img .".format(name=self.name)]
        commands.append("docker run -d -t --name {name} {name}-img {portmaps}".format(
            name=self.name, portmaps=self.get_portmaps()))

        return "\n".join(commands)

    def get_dockerfile(self):
        commands = ["FROM " + self.base, ""]
        ports = []

        for container in self.containers.values():
            ports.extend(list(container.exposed_ports.keys()))
            commands.extend(container.get_container_commands())
            commands.append("")

        commands.append("EXPOSE " + ' '.join(ports))
        return '\n'.join(commands)