FROM jpetazzo/dind
MAINTAINER Taylor "Nekroze" Lawson

RUN docker run -d -p 172.17.42.1:53:53/udp --name skydns crosbymichael/skydns -nameserver 8.8.8.8:53 -domain drydock
RUN docker run -d -v /var/run/docker.sock:/docker.sock --name skydock -link skydns:skydns crosbymichael/skydock -ttl 30 -environment containers -s /docker.sock -domain drydock
RUN docker run -d -p 80:80 -p 443:443 --name nginx -v /etc/nginx/sites-enabled:/etc/nginx/sites-enabled -v /var/log/nginx:/var/log/nginx dockerfile/nginx

RUN apt-get install -y supervisor openssh-server
RUN mkdir -p /var/run/sshd /var/log/supervisor
ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80 443 22
ENTRYPOINT /usr/bin/supervisord -n