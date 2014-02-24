=============================
DryDock
=============================

.. image:: https://badge.fury.io/py/drydock.png
    :target: http://badge.fury.io/py/drydock
    
.. image:: https://travis-ci.org/Nekroze/drydock.png?branch=master
    :target: https://travis-ci.org/Nekroze/drydock

.. image:: https://pypip.in/d/drydock/badge.png
    :target: https://pypi.python.org/pypi/drydock

A Docker cluster construction utility.

DryDock takes a simple (`YAML`_) specification file then can construct and
configure a cluster of `Docker`_ containers. DryDock will automatically
setup a reverse proxy, exposure of ports, and even persistent storage to
allow for easy future upgrading by simply rebuilding the DryDock
specification!

Features
--------

* Simple `YAML`_ configuration.
* Automatic `Docker`_ cluster provisioning/configuration
* `Nginx`_ reverse proxy configuration with HTTPS/SSL support
* Easy setup for persistent volumes.
* Share your DryDock specifications with the world.

TODO
----

* Make a better update path. Remove old containers etc.

.. _Nginx link: http://wiki.nginx.org/
.. _YAML link: http://wikipedia.org/wiki/YAML
.. _Docker link: https://www.docker.io/