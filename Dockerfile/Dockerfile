FROM jpetazzo/dind
MAINTAINER Taylor "Nekroze" Lawson

RUN docker run -d -p 172.17.42.1:53:53/udp --name skydns crosbymichael/skydns -nameserver 8.8.8.8:53 -domain drydock
RUN docker run -d -v /var/run/docker.sock:/docker.sock --name skydock -link skydns:skydns crosbymichael/skydock -ttl 30 -environment containers -s /docker.sock -domain drydock
RUN docker run -d -p 80:80 -p 443:443 --name nginx -v /etc/nginx/certs:/etc/nginx/certs -v /etc/nginx/sites-enabled:/etc/nginx/sites-enabled -v /var/log/nginx:/var/log/nginx dockerfile/nginx
ONBUILD RUN cd /etc/nginx/certs && openssl genrsa -out server.key 2048 && openssl req -new -key server.key -out server.csr && openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

RUN apt-get install -y opensshd supervisor && mkdir -p /var/run/sshd /var/log/supervisor && sed -i 's/Port 22/Port 2222/g' /etc/ssh/sshd_config
ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80 443 2222
ENTRYPOINT CMD /usr/bin/supervisord -n
