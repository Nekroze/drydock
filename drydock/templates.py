"""A collection of templates and rendering functions."""
import subprocess


def get_ip_range(interface="docker0"):
    cmd = "ip address show dev " + interface
    addr = subprocess.check_output(cmd.split()).split()
    ip = addr[addr.index('inet') + 1].split('/')[0]
    return ip.split('.')[:-1] + ['0']


NGINX_UPSTREAM = """upstream {name} {{
    server {skyfqdn};
}}"""

NGINX_HTTP = """server {{
    listen       80;
    server_name  {fqdn};

    access_log  /var/log/nginx/{fqdn}.access.log  combined;
    error_log  /var/log/nginx/{fqdn}.error.log;

    location / {{
        {rules}
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-NginX-Proxy true;
        proxy_redirect off;
        proxy_buffering off;

        proxy_pass http://{skyfqdn}:{port}/;
    }}
}}"""

NGINX_HTTPS = """server {{
    listen 443;
    server_name {fqdn};

    access_log  /var/log/nginx/{fqdn}.access.log  combined;
    error_log  /var/log/nginx/{fqdn}.error.log;

    ssl on;
    ssl_session_timeout 5m;
    ssl_protocols SSLv2 SSLv3 TLSv1;
    ssl_ciphers ALL:!ADH:!EXPORT56:RC4+RSA:+HIGH:+MEDIUM:+LOW:+SSLv2:+EXP;
    ssl_prefer_server_ciphers on;
    ssl_certificate /etc/nginx/certs/server.crt;
    ssl_certificate_key /etc/nginx/certs/server.key;

    location / {{
        {rules}
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-NginX-Proxy true;
        proxy_redirect off;
        proxy_buffering off;

        proxy_pass http://{skyfqdn}:{port}/;
    }}
}}"""


NGINX_RULES_INTERNAL = """deny    {gateway};
        allow   {lan}/24;
        allow   {docker}/24;
        deny    all;
"""


NETWORK = {}


def prepare_networking(lani="eth0", dockeri="docker0",
                       gateway='1', dns="8.8.8.8"):
    """Stores useful network information and renders templates."""
    lan = get_ip_range(lani)
    gateway = lan[:-1] + [gateway]
    docker = get_ip_range(dockeri)
    dockerdns = lan[:-1] + ['1']

    NGINX_RULES_INTERNAL = NGINX_RULES_INTERNAL.format(
        lan=lan, gateway=gateway, docker=docker)

    BASE_CONTAINERS = BASE_CONTAINERS.format(lan=lan, gateway=gateway,
                                             docker=docker, dns=dns,
                                             dockerdns=dockerdns)
    NETWORK["lan"] = lan
    NETWORK["gateway"] = gateway
    NETWORK["docker"] = docker
    NETWORK["dockerdns"] = dockerdns
    NETWORK["dns"] = dns


def render_nginx_config(container):
    """
    Render the nginx reverse proxy configuration for the given container.
    """
    if not container.http_port and not container.https_port:
        return ""

    config = []

    if not container.external:
        rules = NGINX_RULES_INTERNAL
    else:
        rules = ""

    if container.http_port:
        config.append(NGINX_HTTP.format(skyfqdn=container.skyfqdn,
                                        name=container.name,
                                        port=container.http_port,
                                        fqdn=container.fqdn, rules=rules))

    if container.https_port:
        config.append(NGINX_HTTPS.format(skyfqdn=container.skyfqdn,
                                         name=container.name,
                                         port=container.https_port,
                                         fqdn=container.fqdn, rules=rules))

    return '\n'.join(config)


BASE_CONTAINERS = """docker run -d -p {dockerdns}:53:53/udp --name skydns crosbymichael/skydns -nameserver {dns}:53 -domain drydock
docker run -d -v /var/run/docker.sock:/docker.sock --name skydock --dns {dockerdns} --link skydns:skydns crosbymichael/skydock -ttl 30 -environment containers -s /docker.sock -domain drydock
docker run -d -p 80:80 -p 443:443 --name nginx --dns {dockerdns} -v /etc/nginx/certs:/etc/nginx/certs -v /etc/nginx/sites-enabled:/etc/nginx/sites-enabled -v /var/log/nginx:/var/log/nginx dockerfile/nginx
cd /etc/nginx/certs && openssl genrsa -out server.key 2048 && openssl req -new -key server.key -out server.csr && openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt"""


def base_commands():
    """Return the base commands in a list"""
    return [cmd for cmd in BASE_CONTAINERS.split('\n')]