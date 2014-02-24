"""A collection of templates and rendering functions."""

SUPERVISOR_BASE = """
[program:sshd]
command=/usr/sbin/sshd -D
autostart=true
autorestart=true

[program:docker]
command=docker -d -dns 172.17.42.1 -H unix:///var/run/docker.sock -r=false
autostart=true
autorestart=true

[program:skydns]
command=docker start skydns
autostart=true
autorestart=true

[program:skydock]
command=docker start skydock
autostart=true
autorestart=true

[program:nginx]
command=docker start nginx
autostart=true
autorestart=true"""

SUPERVISOR_CONTAINER = """[program:{0}]
command=docker start {0}
autostart=true
autorestart=true
"""

NGINX_UPSTREAM = """upstream {name} {{
    server {skyfqdn};
}}"""

NGINX_HTTP = """server {{
    listen       80;
    server_name  {fqdn};

    {rules}
    access_log  /var/log/nginx/log/{fqdn}.access.log  main;
    error_log  /var/log/nginx/log/{fqdn}.error.log;

    location / {{
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-NginX-Proxy true;
        proxy_redirect off;
        proxy_buffering off;

        proxy_pass https://{name}:{port}/;
    }}
}}"""

NGINX_HTTPS = """server {{
    listen 443;
    server_name {fqdn};

    {rules}
    access_log  /var/log/nginx/log/{fqdn}.access.log  main;
    error_log  /var/log/nginx/log/{fqdn}.error.log;

    ssl on;
    ssl_session_timeout 5m;
    ssl_protocols SSLv2 SSLv3 TLSv1;
    ssl_ciphers ALL:!ADH:!EXPORT56:RC4+RSA:+HIGH:+MEDIUM:+LOW:+SSLv2:+EXP;
    ssl_prefer_server_ciphers on;
    ssl_certificate /etc/nginx/certs/server.crt;
    ssl_certificate_key /etc/nginx/certs/server.key;

    location / {{
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-NginX-Proxy true;
        proxy_redirect off;
        proxy_buffering off;

        proxy_pass https://{name}:{port}/;
    }}
}}"""

NGINX_RULES_INTERNAL = """deny all;
    allow 192.168.1.0/24;
    allow 192.168.0.0/24;
"""


def render_nginx_config(container):
    """
    Render the nginx reverse proxy configuration for the given container.
    """
    if not container.http_port and not container.https_port:
        return ""

    config = [NGINX_UPSTREAM.format(name=container.name,
                                    skyfqdn=container.skyfqdn)]

    if not container.external:
        rules = NGINX_RULES_INTERNAL
    else:
        rules = ""

    if container.http_port:
        config.append(NGINX_HTTP.format(name=container.name,
                                        port=container.http_port,
                                        fqdn=container.fqdn, rules=rules))

    if container.https_port:
        config.append(NGINX_HTTPS.format(name=container.name,
                                         port=container.https_port,
                                         fqdn=container.fqdn, rules=rules))

    return '\n'.join(config)


BASE_CONTAINERS = """docker run -d -p 172.17.42.1:53:53/udp --name skydns crosbymichael/skydns -nameserver 8.8.8.8:53 -domain drydock
docker run -d -v /var/run/docker.sock:/docker.sock --name skydock -link skydns:skydns crosbymichael/skydock -ttl 30 -environment containers -s /docker.sock -domain drydock
docker run -d -p 80:80 -p 443:443 --name nginx -v /etc/nginx/certs:/etc/nginx/certs -v /etc/nginx/sites-enabled:/etc/nginx/sites-enabled -v /var/log/nginx:/var/log/nginx dockerfile/nginx
cd /etc/nginx/certs && openssl genrsa -out server.key 2048 && openssl req -new -key server.key -out server.csr && openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt"""


def base_commands():
    """Return the base commands in a list"""
    return [cmd for cmd in BASE_CONTAINERS.split('\n')]