=======================
Specification Reference
=======================

Information fields are displayed as follows:

Optional field with default value

``info``: ``default``: description

Required field

``info``: description

Sub-Container Specification
---------------------------

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

DryDock Specification
---------------------

**DryDock** can specify any of the of following fields (some of which may
overwrite any sub-containers corresponding field).

``name``: name of resulting Docker_ container.

``base``: ``nekroze/drydock``: base image for resulting drydock.
Must support Docker_ in Docker_ (dind_).

``domain``: domain that all sub containers will server unless specified
otherwise.

``subcontainers``: a list of sub-container specifications.

While technically any sub-container fields can be specified in the top level
**DryDock** specification their behaviour is either unspecified, undefined,
or untested.

.. _dind: http://blog.docker.io/2013/09/docker-can-now-run-within-docker/
.. _YAML: http://wikipedia.org/wiki/YAML
.. _Docker: https://www.docker.io/