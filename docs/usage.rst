========
Usage
========

Primarily DryDock is used to generate a working Dockerfile out of a simple yaml configuration file describing a cluster
of docker containers.

Here is an example of a ``drydock.yaml`` file that will construct ``nekroze.com`` with wordpress and gitlab available
at ``blog.nekroze.com`` and ``lab.nekroze.com``, respectively.

.. code-block:: yaml

name: nekroze.com-1
domain: nekroze.com

subcontainers:

  - name: blog
    base: skxskx/wordpress
    exposed_ports:
        22: 22
    http_port: 80

  - name: lab
    base: crashsystems/gitlab-docker
    exposed_ports:
        22: 22
    http_port: 80