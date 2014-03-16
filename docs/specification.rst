=======================
Specification Reference
=======================

Information fields are displayed as follows:

Optional field with default value

``info``: ``default``: description

Required field

``info``: description

DryDock Specification
---------------------

**DryDock** can specify any of the of following fields (some of which may
overwrite any sub-containers corresponding field).

``name``: name of resulting Docker_ container.

``domain``: domain that all sub containers will server unless specified
otherwise.

``subcontainers``: a list of sub-container specifications.

While technically any sub-container fields can be specified in the top level
**DryDock** specification their behaviour is either unspecified, undefined,
or untested.

Sub-Container Specification
---------------------------

Any container can define the following information.

``name``: name of resulting Docker_ container.

``base``: ``ubuntu``: base image for container.

``domain``: ``none``: domain that subcontainers will serve.

``specification: ``none``: a link to a container specification that will be
used as the base for this container. Any fields defined in this
specification will override the given link's specification. With this docker
container developers can provide its own specification and leave the
implementation fields (ie, domain) to the end user.

``command``: ``none``: if provided this command will be passed to the new
container for its first time setup.

``envs``: ``none``: map of variable names and values to pass to the container.

``external``: ``Yes``: if ``No`` container will allow only lan connections.

``exposed_ports``: ``none``: a set of external to internal port maps.

``http_port``: ``80``: port that serves http for the reverse proxy to point
to.

``https_port``: ``443``: port that serves https for the reverse proxy to
point to.

``volumes``: ``none``: list of paths to be externally available under
``/var/lib/{domain}/{containername}/{volume}``.

``data``: ``No``: if ``Yes`` this container will have an additional volume
map from the hosts ``/var/lib/{domain}/drydock/data`` to the container path
``/mnt/data``.

.. _YAML: http://wikipedia.org/wiki/YAML
.. _Docker: https://www.docker.io/