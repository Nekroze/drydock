FROM jpetazzo/dind
MAINTAINER Taylor "Nekroze" Lawson

RUN apt-get install -y python-pip aufs-tools
RUN pip install drydock

EXPOSE 80 443 2222

ADD ./drypull /usr/local/bin/drypull
ADD ./dryconstruct /usr/local/bin/dryconstruct
ADD ./drysupervise /usr/local/bin/drysupervise
RUN chmod +x /usr/local/bin/drypull /usr/local/bin/dryconstruct /usr/local/bin/drysupervise

CMD drysupervise
