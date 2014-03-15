FROM jpetazzo/dind
MAINTAINER Taylor "Nekroze" Lawson

RUN apt-get install -y python-pip aufs-tools
RUN pip install drydock

EXPOSE 80 443 2222

ADD ./startdocker /usr/local/bin/startdocker
RUN chmod +x /usr/local/bin/startdocker

CMD startdocker && drydock supervise /drydock/specification.yaml
