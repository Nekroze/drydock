"""DryDock cluster specification."""
from . import templates


class Container(object):
    """A docker container specification."""
    def __init__(self, name, base="ubuntu", exposed_ports=None, external=False,
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
        self.commands = []
        self.skyfqdn = '.'.join([self.name, self.base.split('/')[-1],
                                 "containers", "drydock"])

    def set_domain(self, domain):
        """Set fqdn and domain."""
        self.domain = domain
        if self.name == "root":
            self.fqdn = self.domain
        else:
            self.fqdn = self.name + '.' + self.domain

    def get_container_commands(self):
        """
        Return a list of commands required to construct and use this
        container specification.
        """
        commands = []
        run = 'docker run -d'.split(' ')

        run.append("--name {0}".format(self.name))

        for external in sorted(self.exposed_ports.keys()):
            run.append("-p {0}:{1}".format(external,
                                           self.exposed_ports[external]))

        for path in self.volumes:
            run.append("-v /var/lib/{0}{1}:{1}".format(self.name, path))

        run.append(self.base)
        commands.append("RUN " + ' '.join(run))
        commands.append(
            "ADD supervisor/{0}.conf /etc/supervisor/conf.d/{0}.conf".format(
                self.name))

        if self.http_port or self.https_port:
            commands.append(
                "ADD sites/{0} /etc/nginx/sites-enabled/{0}".format(self.fqdn))

        commands.extend(self.commands)
        return '\n'.join(commands)

    def get_supervisor_config(self):
        """
        Write this containers supervisor configuration file to
        ``./supervisor/{Container.name}.conf``.
        """
        return """[program:{0}]
command=docker start {0}
autostart=true
autorestart=true""".format(self.name)

    def get_nginx_config(self):
        """
        Write this containers nginx site configuration to
        ``./sites/{Container.fqdn}``
        """
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
        """Set fqdn and domain."""
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

    def get_portmaps(self):
        """return docker args for subcontainer port maps."""
        template = "-p {0}:{1}"
        portmaps = [template.format("80", "80"), template.format("443", "443")]

        for name in sorted(self.containers.keys()):
            container = self.containers[name]
            for port in sorted(container.exposed_ports.keys()):

                portmap = template.format(port, port)
                if portmap not in portmaps:
                    portmaps.append(portmap)

        return ' '.join(portmaps)

    def get_volumemaps(self):
        """return docker args for subcontainer volume maps."""
        volumes = []

        for volume in self.volumes:
            volumes.append("-v {statedir}{volume}:{volume}".format(
                statedir="/var/lib/" + self.name, volume=volume))

        for name in sorted(self.containers.keys()):
            container = self.containers[name]

            for volume in container.volumes:
                volumes.append("-v {statedir}/{name}{volume}:{volume}".format(
                    statedir="/var/lib/" + self.name, name=container.name,
                    volume=volume))

        return ' ' + ' '.join(set(volumes))

    def get_docker_commands(self):
        """Get commands required to build and run the final product."""
        commands = ["docker build -t {name}-img .".format(name=self.name),
                    "docker run -privileged -d -t --name {0} {0}-img {1}{2}".format(
                        self.name, self.get_portmaps(), self.get_volumemaps())]
        return "\n".join(commands)

    def get_dockerfile(self):
        """Render the dockerfile according to specifications."""
        commands = ["FROM " + self.base, ""]
        ports = [80, 443]
        volumes = []

        for name in sorted(self.containers.keys()):
            container = self.containers[name]

            ports.extend(sorted(list(container.exposed_ports.keys())))
            commands.append(container.get_container_commands())
            commands.append("")

            for volume in container.volumes:
                volumes.append("/var/lib/{0}{1}".format(container.name,
                                                        volume))

        commands.append("EXPOSE " + ' '.join([str(port) for port in ports]))

        volumes = ['"{0}"'.format(volume) for volume in volumes]
        if volumes:
            commands.append("VOLUME [{0}]".format(", ".join(set(volumes))))

        return '\n'.join(commands)
