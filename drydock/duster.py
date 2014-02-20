"""DryDock cluster specification."""
from . import templates
import os


class Container(object):
    """A docker container specification."""
    def __init__(self, name, base="ubuntu", exposed_ports=None,
                 external=False, http_port=0, https_port=0, domain=""):
        self.name = name
        self.domain = domain
        self.base = base
        self.exposed_ports = {}
        self.exposed_ports.update(exposed_ports)
        self.http_port = 0
        self.https_port = 0
        self.external = external
        self.commands = []
        self.skyfqdn = '.'.join([self.name, self.base.split('/')[-1], "containers", "drydock"])
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
        return commands.extend(self.commands)

    def write_supervisor_config(self):
        """Write this containers supervisor configuration file to `./supervisor/{Container.name}.conf`"""
        if not os.path.exists("supervisor"):
            os.makedirs("supervisor")

        with open("supervisor/{0}.conf".format(self.name), 'w') as config:
            config.write("""[program:{0}]
command=docker start {0}
autostart=true
autorestart=true""".format(self.name))

    def write_nginx_config(self, domain):
        """Write this containers nginx site configuration to `./sites/{Container.fqdn}`"""
        if not self.http_port and not self.https_port:
            return False

        config = [templates.NGINX_UPSTREAM.format(name=self.name, skyfqdn=self.skyfqdn)]

        if self.http_port:
            config.append(templates.NGINX_HTTP.format(name=self.name, port=self.http_port, fqdn=self.fqdn))

        if self.https_port:
            config.append(templates.NGINX_HTTPS.format(name=self.name, port=self.https_port, fqdn=self.fqdn))

        if not os.path.exists("sites"):
            os.makedirs("sites")

        with open("sites/{0}".format(self.fqdn), 'w') as nginx:
            nginx.write('\n'.join(config))


class MetaContainer(Container):
    """A container that stores containers."""
    def __init__(self, name, domain, subcontainers, base="nekroze/drydock"):
        super(MetaContainer, self).__init__(name=name, base=base, domain=domain)
        self.containers = {}
        self.reverse_proxies = {}

        for sub in subcontainers:
            self.add_container(Container(**sub))

    def add_container(self, container):
        """Add the given container object to this meta container."""
        self.containers[container.name] = container
        self.exposed_ports.update(container.exposed_ports)

        fqdn = container.name + '.' + self.domain
        self.reverse_proxies[fqdn] = {
            "skyfqdn": container.skyfqdn,
            "external": container.external,
            "http": container.http_port,
            "https": container.https_port
        }