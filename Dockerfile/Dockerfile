FROM jpetazzo/dind
MAINTAINER Taylor "Nekroze" Lawson

RUN apt-get install -y openssh-server supervisor python-pip
RUN mkdir -p /var/run/sshd /var/log/supervisor
RUN sed -i 's/Port 22/Port 2222/g' /etc/ssh/sshd_config
RUN pip install drydock

ADD supervisord.conf /etc/supervisord.conf

EXPOSE 80 443 2222
ENTRYPOINT CMD /usr/bin/supervisord -n
