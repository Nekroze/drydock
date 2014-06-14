"""A collection of templates and rendering functions."""
import subprocess


def get_ip_range(interface="docker0"):
    cmd = "ip address show dev " + interface
    addr = subprocess.check_output(cmd.split()).split()
    ip = addr[addr.index('inet') + 1].split('/')[0]
    return ip.split('.')[:-1] + ['0']


TEMPLATES = {"NGINX": {}, "BASE": {}}

TEMPLATES["BASE"]["CONTAINERS"] = """docker run -d -p {dockerdns}:53:53/udp --name skydns crosbymichael/skydns -nameserver {dns}:53 -domain drydock
docker run -d -v /var/run/docker.sock:/docker.sock --name skydock --dns {dockerdns} --link skydns:skydns crosbymichael/skydock -ttl 30 -environment containers -s /docker.sock -domain drydock
docker run -d -p 80:80 -p 443:443 --name nginx --dns {dockerdns} -v /etc/nginx/certs:/etc/nginx/certs -v /etc/nginx/sites-enabled:/etc/nginx/sites-enabled -v /var/log/nginx:/var/log/nginx dockerfile/nginx
cd /etc/nginx/certs && openssl genrsa -out server.key 2048 && openssl req -new -key server.key -out gitlab.csr && openssl x509 -req -days 365 -in gitlab.csr -signkey server.key -out gitlab.crt"""

TEMPLATES["NGINX"]["HEADER"] = """events {
    worker_connections 1024;
    use epoll;
}"""

TEMPLATES["NGINX"]["UPSTREAM"] = """upstream {name} {{
    server {skyfqdn};
}}"""

TEMPLATES["NGINX"]["HTTP"] = """server {{
    listen       80;
    server_name  {fqdn};

    access_log  /var/log/nginx/{fqdn}.access.log  combined;
    error_log  /var/log/nginx/{fqdn}.error.log;

    resolver {dns} valid=5s;
    resolver_timeout 5s;

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

TEMPLATES["NGINX"]["HTTPS"] = """server {{
    listen       443;
    server_name  {fqdn};

    access_log  /var/log/nginx/{fqdn}.access.log  combined;
    error_log  /var/log/nginx/{fqdn}.error.log;

    resolver {dns} valid=5s;
    resolver_timeout 5s;

    ssl                         on;
    ssl_session_timeout         10m;
    ssl_protocols               SSLv3 TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers                 RC4:HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers   on;
    ssl_certificate /etc/nginx/certs/server.crt;
    ssl_certificate_key /etc/nginx/certs/server.key;

    location / {{
        {rules}
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
        proxy_set_header        Accept-Encoding   "";
        proxy_set_header        Host            $host;
        proxy_set_header        X-Real-IP       $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header        X-Forwarded-Proto $scheme;
        add_header              Front-End-Https   on;
        proxy_redirect off;

        proxy_pass http://{skyfqdn}:{port}/;
    }}
}}"""


TEMPLATES["NGINX"]["RULES"] = """deny    {gateway};
        allow   {lan}/24;
        allow   {docker}/24;
        deny    all;
"""


NETWORK = {}


def prepare_networking(lani="eth0", dockeri="docker0",
                       gateway='1', dns="8.8.8.8"):
    """Stores useful network information and renders templates."""
    lanip = get_ip_range(lani)
    lan = '.'.join(lanip)
    gateway = '.'.join(lanip[:-1] + [gateway])
    dockerip = get_ip_range(dockeri)
    docker = '.'.join(dockerip)
    dockerdns = '.'.join(dockerip[:-1] + ['1'])

    TEMPLATES["NGINX"]["RULES"] = TEMPLATES["NGINX"]["RULES"].format(
        lan=lan, gateway=gateway, docker=docker)

    TEMPLATES["BASE"]["CONTAINERS"] = TEMPLATES["BASE"]["CONTAINERS"].format(
        lan=lan, gateway=gateway, docker=docker, dns=dns, dockerdns=dockerdns)
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
        rules = TEMPLATES["NGINX"]["RULES"]
    else:
        rules = ""

    if container.http:
        config.append(TEMPLATES["NGINX"]["HTTP"].format(
            skyfqdn=container.skyfqdn, name=container.name, dns=NETWORK["dns"],
            port=container.http_port, fqdn=container.fqdn, rules=rules))

    if container.https:
        config.append(TEMPLATES["NGINX"]["HTTPS"].format(
            skyfqdn=container.skyfqdn, name=container.name, dns=NETWORK["dns"],
            port=container.https_port, fqdn=container.fqdn, rules=rules))

    return '\n'.join(config)


def base_commands():
    """Return the base commands in a list"""
    return [cmd for cmd in TEMPLATES["BASE"]["CONTAINERS"].split('\n')]