"""
Tests for `drydock.duster` module and MetaContainer object.
"""
import pytest
from drydock.duster import MetaContainer
import yaml


class TestContainer(object):
    config = """
name: nekroze.com-1
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

        assert meta.name == "nekroze.com-1"
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

    def test_docker_commands(self):
        meta = MetaContainer(**yaml.load(self.config))

        assert meta.get_docker_commands() == """docker build -t nekroze.com-1-img .
docker run -d -t --name nekroze.com-1 nekroze.com-1-img -p 80:80 -p 443:443 -p 22:22 -p 2222:2222 -v /var/lib/nekroze.com-1/blog/var/lib/mysql:/var/lib/mysql"""

    def test_dockerfile(self):
        meta = MetaContainer(**yaml.load(self.config))

        assert meta.get_dockerfile() == """FROM nekroze/drydock

RUN docker run -d --name blog -p 22:22 -p 2222:222 -v /var/lib/blog/var/lib/mysql:/var/lib/mysql nekroze/wordpress
ADD supervisor/blog.conf /etc/supervisor/conf.d/blog.conf
ADD sites/blog.nekroze.com /etc/nginx/sites-enabled/blog.nekroze.com

RUN docker run -d --name root nekroze/drupal
ADD supervisor/root.conf /etc/supervisor/conf.d/root.conf
ADD sites/nekroze.com /etc/nginx/sites-enabled/nekroze.com

EXPOSE 80 443 22 2222
VOLUME ["/var/lib/blog/var/lib/mysql"]"""