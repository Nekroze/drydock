=============================
DryDock
=============================

.. image:: https://badge.fury.io/py/drydock.png
    :target: http://badge.fury.io/py/drydock
    
.. image:: https://travis-ci.org/Nekroze/drydock.png?branch=master
    :target: https://travis-ci.org/Nekroze/drydock

.. image:: https://pypip.in/d/drydock/badge.png
    :target: https://crate.io/packages/drydock?version=latest


A Docker cluster construction utility.

DryDock can convert a simple configuration file into a Dockerfile
(and accompanying configs) that when built will run a cluster of docker
containers. The end product will automatically setup a reverse proxy, exposure
of ports, and even persistent storage to allow for easy future upgrading by
simply rebuilding the DryDock specification!

Features
--------

* Simple configuration.
* Automatic Docker cluster provisioning/configuration
* Nginx reverse proxy configuration with HTTPS/SSL support
* Easy setup for persistent volumes.
* Share your DryDock Docker clusters with the world.
