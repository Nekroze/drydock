=======
DryDock
=======

.. image:: https://badge.fury.io/py/drydock.png
    :target: http://badge.fury.io/py/drydock
    
.. image:: https://travis-ci.org/Nekroze/drydock.png?branch=master
    :target: https://travis-ci.org/Nekroze/drydock

.. image:: https://pypip.in/d/drydock/badge.png
    :target: https://pypi.python.org/pypi/drydock

A Docker cluster construction utility.

DryDock takes a simple (YAML_) specification file then can construct and
configure a cluster of Docker_ containers. DryDock will automatically
setup a reverse proxy, exposure of ports, and even persistent storage to
allow for easy future upgrading by simply rebuilding the DryDock
specification!

Features
--------

* Simple YAML_ configuration.
* Automatic Docker_ cluster provisioning/configuration
* Nginx_ reverse proxy configuration with HTTPS/SSL support
* Easy setup for persistent volumes.
* Share your DryDock specifications with the world.
* Container supervisor utilizing the Docker_ API.

TODO
----

* Provide a better update path, specific update commands, custom pre-post.
* Container monitoring, ensure a container is working else reconstruct it.
* Better support for stateless-ness and volumes
* Better unittest coverage.
* Ability to provide a custom docker images repository for master containers.
* An external facing DNS server or config generation.
* Control over a master container cluster, Drydock as a Service?.
* Web interface for control, logging and monitoring. Far future.

.. _Nginx: http://wiki.nginx.org/
.. _YAML: http://wikipedia.org/wiki/YAML
.. _Docker: https://www.docker.io/