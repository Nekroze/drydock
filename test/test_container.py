"""
Tests for `drydock.duster` module and Container object.
"""
import pytest
from drydock.duster import Container
from drydock.templates import NETWORK
import yaml


class TestContainer(object):
    config = """
name: blog
base: nekroze/wordpress
domain: nekroze.com
command: crump
envs:
    DB: 123
exposed_ports:
    22: 22
    2222: 222
http_port: 8081
https_port: 4431
external: No
"""

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

    def test_nginx(self):
        container = Container(**yaml.load(self.config))
        NETWORK["dns"] = "172.17.42.1"
        container.http = True
        container.https = True
        expected = """server {
    listen       80;
    server_name  blog.nekroze.com;

    access_log  /var/log/nginx/blog.nekroze.com.access.log  combined;
    error_log  /var/log/nginx/blog.nekroze.com.error.log;

    resolver 172.17.42.1 valid=5s;
    resolver_timeout 5s;

    location / {
        deny    {gateway};
        allow   {lan}/24;
        allow   {docker}/24;
        deny    all;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-NginX-Proxy true;
        proxy_redirect off;
        proxy_buffering off;

        proxy_pass http://blog.wordpress.containers.drydock:8081/;
    }
}
server {
    listen       443;
    server_name  blog.nekroze.com;

    access_log  /var/log/nginx/blog.nekroze.com.access.log  combined;
    error_log  /var/log/nginx/blog.nekroze.com.error.log;

    resolver 172.17.42.1 valid=5s;
    resolver_timeout 5s;

    ssl                         on;
    ssl_session_timeout         10m;
    ssl_protocols               SSLv3 TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers                 RC4:HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers   on;
    ssl_certificate /etc/nginx/certs/server.crt;
    ssl_certificate_key /etc/nginx/certs/server.key;

    location / {
        deny    {gateway};
        allow   {lan}/24;
        allow   {docker}/24;
        deny    all;

        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
        proxy_set_header        Accept-Encoding   "";
        proxy_set_header        Host            $host;
        proxy_set_header        X-Real-IP       $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header        X-Forwarded-Proto $scheme;
        add_header              Front-End-Https   on;
        proxy_redirect off;

        proxy_pass http://blog.wordpress.containers.drydock:4431/;
    }
}"""
        assert container.get_nginx_config() == expected

    def test_container_commands(self):
        container = Container(**yaml.load(self.config))

        assert container.get_docker_command() == \
               "docker run -d --dns {dockerdns} --name blog -h blog.nekroze.com -p 22:22 -p 2222:222 -v /etc/timezone:/etc/timezone:ro -e \"DB=123\" nekroze/wordpress crump"