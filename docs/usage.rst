========
Usage
========

Primarily DryDock is used to generate a working Dockerfile out of a simple yaml configuration file describing a cluster
of docker containers.

Here is an example of a ``drydock.yaml`` file that will construct ``nekroze.com`` with wordpress and gitlab available
at ``blog.nekroze.com`` and ``lab.nekroze.com``, respectively. Finally the config describes a special `root` container
that serves the root of the domain, in this case ``nekroze.com`` gets passed to the ``root`` sub-container running
drupal.

.. code-block:: yaml

    name: nekroze.com-1
    domain: nekroze.com

    subcontainers:

      - name: blog
        base: skxskx/wordpress
        exposed_ports:
            2222: 22
        http_port: 80

      - name: lab
        base: crashsystems/gitlab-docker
        exposed_ports:
            22: 22
        http_port: 80

      - name: root
        base: moul/drupal
        exposed_ports:
            2221: 22
        http_port: 80