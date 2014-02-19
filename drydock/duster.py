"""DryDock cluster specification"""


def parse(config):
    spec = MetaContainer("nekroze/drydock", config["name"], config["domain"])
    return spec


class Container(object):
    """A docker container specification."""
    def __init__(self, base, name):
        self.name = name
        self.base = base
        self.exposed_ports = []
        self.http_port = 0
        self.https_port = 0


class MetaContainer(Container):
    """A container that stores containers."""
    def __init__(self, base, name, domain):
        super(MetaContainer, self).__init__(base, name)
        self.domain = domain
        self.containers = []