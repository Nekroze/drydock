=====
Usage
=====

**DryDock** has multiple functions, the end goal of which is to setup and
configure a cluster of Docker_ containers.

Master
------

.. warning::

    Currently master containers do not function correctly. There are issues
    with running multiple commands on the first run. There also seems to be
    an issue with running ``Skydock`` the docker dns inside a docker
    container.

The ``master`` command will construct and run a new Docker_ container under
the given name based upon ``nekroze/drydock`` . This container is setup and
ready to use **DryDock** to run a cluster of Docker_ containers in a Docker_
container (dind_). This is designed to easily contain a **DryDock** cluster
but is not required.

By default the master container will take over the host ports; 80, 443,
for; HTTP, and HTTPS. This can be customized by providing the root
specification a ``http_port`` and ``https_port`` respectively. If the
specification describes any exposed ports for sub-containers the external
ports for those will also be exposed through the master container.

Once a master container has been constructed it will be stored as an image
in the hosts docker repository and **DryDock** will provide the user with
the command required to run that specific container. It may be worth adding
the docker ``--rm=true`` switch to the provided command. using this in an
upstart script for example would mean that each boot or restart of the
master container will be fresh from the original image that was created.

.. note::

    Setting up a **DryDock** master container is entirely optional.

.. warning::

    The resulting master container runs in ``--privileged`` mode and retains
    all security concerns of such a Docker_ container.

Prepare
-------

This command will setup a few Docker_ containers, generate an ssl
certificate, and must be run before running ``construct`` on a specification.

The following containers will be setup and run:

#. ``skydns``: Small dns server.
#. ``skydock``: Docker skydns registry.
#. ``nginx``: An nginx powered reverse proxy container.

The ``nginx`` container will have a volume mapped to the hosts
``/etc/nginx/sites-enabled`` directory for the matching ``nginx`` directory.

Construct
---------

The main function for **DryDock**, ``construct``, takes a YAML_ specification file
and will create the required configuration files (supervisor, and nginx)
before running and naming containers as defined in the specification.

Here is an example of a **DryDock** specification file that will construct
``nekroze.com`` with *wordpress* and *gitlab* available at ``blog.nekroze.com``
and ``lab.nekroze.com``. Finally the config describes a special
``root`` container that serves the root of the domain, in this case
``nekroze.com`` gets passed to the ``root`` sub-container running *drupal*.

.. code-block:: yaml

    name: nekroze.com-1
    domain: nekroze.com

    subcontainers:

      - name: blog
        base: skxskx/wordpress
        exposed_ports:
            2222: 22
        http_port: 80
        volumes: [/var/lib/mysql]

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


The YAML_ specification file consists of two main parts; cluster information,
and container specification. Together these define a *DryDock Specification*
which gets constructed into running Docker_ containers and accompanying
configuration files!

All peristant data should be stored in ``/var/lib/{domain}/`` where domain
is the specifications domain

.. note::

    This command assumes that both Docker_ and supervisor are currently
    installed on the system.


Pull
----

This command is used almost identically to the ``construct`` and
``deconstruct`` command and will download all of the base images in the
given specification. This can be useful for caching and or testing.


Supervise
---------

This is a supervisor for a **DryDock** container cluster and can be used to
ensure sub-container uptime.

.. note::

    When using a master container, its default entrypoint command will be to
    supervise the given specification.

Deconstruct
-----------

The ``deconstruct`` command is used the same way as the ``construct``
command, however it will remove any thing created by the corrosponding
``construct`` command.

.. _dind: http://blog.docker.io/2013/09/docker-can-now-run-within-docker/
.. _YAML: http://wikipedia.org/wiki/YAML
.. _Docker: https://www.docker.io/
