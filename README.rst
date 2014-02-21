=============================
Dry Dock
=============================

.. image:: https://badge.fury.io/py/drydock.png
    :target: http://badge.fury.io/py/drydock
    
.. image:: https://travis-ci.org/Nekroze/drydock.png?branch=master
    :target: https://travis-ci.org/Nekroze/drydock

.. image:: https://pypip.in/d/drydock/badge.png
    :target: https://crate.io/packages/drydock?version=latest


A Docker cluster construction utility.

Dry Dock can convert a simple configuration file into a Dockerfile and accomponying files that when built will run a
cluster of docker containers that will automatically setup with reverse proxying, exposure of ports and even persistant
storage to allow for easy future upgrading by simply rebuilding the DryDock Dockerfile!

Features
--------

* Automatic Docker cluster provisioning
* Nginx reverse proxy configuration with HTTPS/SSL support
