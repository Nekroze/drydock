========
Usage
========

Primarily DryDock is used to generate a working Dockerfile out of a simple
yaml specification file describing a cluster of docker containers.

For example:

    $ drydock ./nekroze.com.yaml

Here is an example of a DryDock specification file that will construct
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


The yaml specification file consists of two main parts; cluster information,
and container specification. Together these define a *DryDock Specification*
which gets constructed into a **Dockerfile** and accompanying configuration
files along with a ``build.sh`` script that can be used to construct and run
your new docker cluster!

drydock.yaml Specifications
---------------------------

Information fields are displayed as follows:

Optional field with default value

``info``: ``[default]``: description

Required field

``info``: description

Sub-Container Specification:
++++++++++++++++++++++++++++

Any container can define the following information.

``name``: name of resulting docker container.

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

DryDock can specify any of the of following fields (some of which may
overwrite any sub-containers corresponding field).

``name``: name of resulting docker container.

``base``: ``nekroze/drydock``: base image for resulting drydock.
Must support docker in docker.

``domain``: domain that all sub containers will server unless specified
otherwise.

``subcontainers``: a list of sub-container specifications.

While technically any sub-container fields can be specified in the top level
*DryDock* specification their behaviour is either unspecified, undefined,
or untested.