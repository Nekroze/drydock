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
    if not container.http_port and not container.https_port:
        return ""

    config = [NGINX_UPSTREAM.format(name=container.name, skyfqdn=container.skyfqdn)]

    if not container.external:
        rules = NGINX_RULES_INTERNAL
    else:
        rules = ""

    if container.http_port:
        config.append(NGINX_HTTP.format(name=container.name, port=container.http_port,
                                        fqdn=container.fqdn, rules=rules))

    if container.https_port:
        config.append(NGINX_HTTPS.format(name=container.name, port=container.https_port,
                                         fqdn=container.fqdn,rules=rules))

    return '\n'.join(config)