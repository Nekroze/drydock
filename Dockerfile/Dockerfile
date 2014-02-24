FROM jpetazzo/dind
MAINTAINER Taylor "Nekroze" Lawson

RUN apt-get install -y opensshd supervisor && mkdir -p /var/run/sshd /var/log/supervisor && sed -i 's/Port 22/Port 2222/g' /etc/ssh/sshd_config
ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80 443 2222
ENTRYPOINT CMD /usr/bin/supervisord -n
