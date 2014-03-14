"""A collection of templates and rendering functions."""

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

NGINX_RULES_INTERNAL = """deny    192.168.1.1;
        allow   192.168.1.0/24;
        allow   172.17.42.0/24;
        deny    all;
"""


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


BASE_CONTAINERS = """docker run -d -p 172.17.42.1:53:53/udp --name skydns crosbymichael/skydns -nameserver 8.8.8.8:53 -domain drydock
docker run -d -v /var/run/docker.sock:/docker.sock --name skydock --dns 172.17.42.1 --link skydns:skydns crosbymichael/skydock -ttl 30 -environment containers -s /docker.sock -domain drydock
docker run -d -p 80:80 -p 443:443 --name nginx --dns 172.17.42.1 -v /etc/nginx/certs:/etc/nginx/certs -v /etc/nginx/sites-enabled:/etc/nginx/sites-enabled -v /var/log/nginx:/var/log/nginx dockerfile/nginx
cd /etc/nginx/certs && openssl genrsa -out server.key 2048 && openssl req -new -key server.key -out server.csr && openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt"""


def base_commands():
    """Return the base commands in a list"""
    return [cmd for cmd in BASE_CONTAINERS.split('\n')]