"""
Tests for `drydock.duster` module and MetaContainer object.
"""
import pytest
from drydock.duster import MetaContainer
import yaml


class TestMetaContainer(object):
    config = """
name: nekroze.com
domain: nekroze.com

subcontainers:

  - name: blog
    base: nekroze/wordpress
    exposed_ports:
        22: 22
        2222: 222
    http_port: 8081
    https_port: 4431
    external: Yes
    volumes: [/var/lib/mysql]

  - name: root
    base: nekroze/drupal
    http_port: 80
    https_port: 443
"""

    def test_construction(self):
        meta = MetaContainer(**yaml.load(self.config))

        assert meta.name == "nekroze.com"
        assert meta.domain == "nekroze.com"
        assert meta.fqdn == "nekroze.com"

    def test_subcontainer(self):
        meta = MetaContainer(**yaml.load(self.config))

        assert len(meta.containers.keys()) == 2
        assert "blog" in meta.containers.keys()
        assert "root" in meta.containers.keys()

        subcontainer = meta.containers["blog"]

        assert subcontainer.name == "blog"
        assert subcontainer.base == "nekroze/wordpress"
        assert subcontainer.domain == "nekroze.com"
        assert subcontainer.exposed_ports == {22:22, 2222:222}
        assert subcontainer.http_port == 8081
        assert subcontainer.https_port == 4431
        assert subcontainer.external is True
        assert subcontainer.skyfqdn == "blog.wordpress.containers.drydock"
        assert subcontainer.fqdn == "blog.nekroze.com"

    def test_root_subcontainer(self):
        subcontainer = MetaContainer(**yaml.load(self.config)).containers["root"]

        assert subcontainer.domain == "nekroze.com"
        assert subcontainer.fqdn == "nekroze.com"