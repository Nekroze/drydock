FROM jpetazzo/dind
MAINTAINER Taylor "Nekroze" Lawson

RUN apt-get install -y python-pip aufs-tools
RUN pip install drydock

ENV PORT 4444
EXPOSE 80 443 2222 4444

ADD ./startdocker /usr/local/bin/startdocker
RUN chmod +x /usr/local/bin/startdocker

CMD startdocker && drydock supervise /drydock/specification.yaml
