"""
Tests for `drydock.duster` module.
"""
import pytest
from drydock.duster import Container, MetaContainer
import yaml


class TestContainer(object):
    config = """---
name: blog
base: nekroze/wordpress
domain: nekroze.com
exposed_ports:
    22: 22
    2222: 222
http_port: 8081
https_port: 4431
external: No
..."""

    def test_construction(self):
        container = Container(**yaml.load(self.config))
        assert container.name == "blog"
        assert container.base == "nekroze/wordpress"
        assert container.domain == "nekroze.com"
        assert container.exposed_ports == {22:22, 2222:222}
        assert container.http_port == 8081
        assert container.https_port == 4431
        assert container.external is False
        assert container.skyfqdn == "blog.wordpress.containers.drydock"
        assert container.fqdn == "blog.nekroze.com"