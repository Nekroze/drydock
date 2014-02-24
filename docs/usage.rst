========
Usage
========

**DryDock** has multiple functions, the end goal of which is to setup and
configure a cluster of Docker_ containers.

.. code::

    $ drydock -h
    DryDock v0.1.3

    Usage:
        drydock construct <specification>
        drydock prepare
        drydock master [options] <name>
        drydock --help | --version

    Options:
        -p --http=<http>        HTTP Port. [default: 80]
        -l --https=<https>      HTTPS Port. [default: 443]
        -s --ssh=<ssh>          SSH Port. [default: 2222]

        -h --help               Show this screen.
        -v --version            Show current version.

    Commands:
        construct   Construct the given specification.
        prepare     Prepare docker for constructing a drydock specification.
        master      Create a container that can run a drydock specification.

    DryDock takes a simple (YAML) specification file then can construct and
    configure a cluster of Docker containers. DryDock will automatically setup a
    reverse proxy, exposure of ports, and even persistent storage to allow for
    easy future upgrading by simply rebuilding the DryDock specification!

    For documentation go to http://dry-dock.readthedocs.org/

Master
------

The ``master`` command will construct and run a new Docker_ container under
the given name based upon ``nekroze/drydock``. This container is setup and
ready to use **DryDock** to run a cluster of Docker_ containers in a Docker_
container. This is designed to easily contain a **DryDock** cluster but is not
required.

By default the master container will take over the host ports; 80, 443,
and 2222 by default for; HTTP, HTTPS, and SSH.

Once a master container has been constructed and is running the user should
SSH into the master container and use the ``prepare`` command before
constructing your specification within the master container with the
``construct`` command.

.. note::

    Setting up a **DryDock** master container is entirely optional.

.. warning::

    The resulting master container runs in ``-privileged`` mode and retains
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

.. note::

    This command assumes that both Docker_ and supervisor are currently
    installed on the system.

.. warning::

    ``construct`` will overwrite the configuration files on the host at
    ``/etc/supervisord.conf`` and
    ``/etc/nginx/sites-enabled/domain.com`` where ``domain.com`` is the
    domain for specified in the DryDock cluster specification

Specification Reference
-----------------------

Information fields are displayed as follows:

Optional field with default value

``info``: ``default``: description

Required field

``info``: description

Sub-Container Specification:
++++++++++++++++++++++++++++

Any container can define the following information.

``name``: name of resulting Docker_ container.

``base``: ``ubuntu``: base image for container.

``domain``: ``none``: domain that subcontainers will serve.

``external``: ``true``: if false will allow only lan connections.

``exposed_ports``: ``none``: a set of external to internal port maps.

``http_port``: ``80``: port that serves http for the reverse proxy to point
to.

``https_port``: ``443``: port that serves https for the reverse proxy to
point to.

``volumes``: ``none``: list of paths to be externally available under
``/var/lib/{name}/{containername}/{volume}``.

DryDock Specification:
++++++++++++++++++++++

**DryDock** can specify any of the of following fields (some of which may
overwrite any sub-containers corresponding field).

``name``: name of resulting Docker_ container.

``base``: ``nekroze/drydock``: base image for resulting drydock.
Must support Docker_ in Docker_.

``domain``: domain that all sub containers will server unless specified
otherwise.

``subcontainers``: a list of sub-container specifications.

While technically any sub-container fields can be specified in the top level
**DryDock** specification their behaviour is either unspecified, undefined,
or untested.

.. _YAML: http://wikipedia.org/wiki/YAML
.. _Docker: https://www.docker.io/
