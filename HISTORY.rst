.. :changelog:

History
-------

0.5.14 (17-03-2014)
+++++++++++++++++++

* Changed: ``supervise`` will no longer reconstruct nginx at start.
* Changed: moved full master and cluster container construction to
construction of master image not first time run run.
* Changed: master images will now have ``-master`` appended to the end of
their name
* Changed: master images will now be named based on the specification name
not domain, as will their location in ``/var/lib/..``.
* Fix: Attempted to provide a better final run command for the master image.

0.5.13 (17-03-2014)
+++++++++++++++++++

* Changed: only construct master cluster when supervising.

0.5.12 (17-03-2014)
+++++++++++++++++++

* Added: new master container scripts to manage drydock cluster.

0.5.11 (16-03-2014)
+++++++++++++++++++

* Fix: disabled nginx event config.

0.5.10 (16-03-2014)
+++++++++++++++++++

* Fix: properly wrap final master command in qoutes for bash.

0.5.9 (16-03-2014)
++++++++++++++++++

* Fix: each image only gets pulled once via the pull command.
* Fix: more specific nginx config for use with skydock.

0.5.8 (16-03-2014)
++++++++++++++++++

* Changed: The shared data directory to map
``/var/lib/{domain}/drydock/data`` to the containers ``/mnt/data``.
* Added: Shared data container now works for master containers.

0.5.7 (16-03-2014)
++++++++++++++++++

* Changed: Moved master container prepare to first time run.

0.5.6 (16-03-2014)
++++++++++++++++++

* Fix: only create nginx configs where needed.

0.5.5 (16-03-2014)
++++++++++++++++++

* Changed: master containers only pull on creation and will construct at
first run.

0.5.4 (16-03-2014)
++++++++++++++++++

* Fix: volume mapped master containers drydock volume for persistance.

0.5.3 (16-03-2014)
++++++++++++++++++

* Added: display of final master container run command to end user.

0.5.2 (16-03-2014)
++++++++++++++++++

* Fix: master containers nginx sites are now read write.

0.5.1 (15-03-2014)
++++++++++++++++++

* Added: Customize your network interfaces, ips, and dns from cli.
* Fix: cleaned up template storage to allow manipulation.

0.5.0 (15-03-2014)
++++++++++++++++++

.. warning::
This release has a major emphasis on the ``master`` command and containers
and is released early to facilitate testing.

* Changed: ``master`` command now takes a specification to automatically
build it.
* Removed: any usage of ``supervisord`` in favor of the new
``drydock supervisor``.

0.4.3 (12-03-2014)
++++++++++++++++++

* Fix: use ``--name`` for naming containers for future proofing.
* Fix: use ``--dns`` for future proofing.

0.4.2 (11-03-2014)
++++++++++++++++++

* Fix: allow self connections to the host when nginx blocks external.

0.4.1 (09-03-2014)
++++++++++++++++++

* Fix: check for config files before removing them.
* Fix: ``supervise`` command will now recreate the nginx container each run.

0.4.0 (08-03-2014)
++++++++++++++++++


* Added: ``supervise`` command line command. DryDock has its own supervisor!
* Added: ``start`` and ``stop`` command line commands.
* Added: ``data`` in subcontainer specification maps volumes at
``/mnt/drydock``.
* Fix: All containers are passed their FQDN as their hostname
* Fix: ``pull`` command also grabs the containers required for the
``prepare`` command.
* Fix: Pass host timezone to subcontainers.
* Fix: volumes now go map to ``/var/lib/{domain}/{name}/``.

0.3.0 (28-02-2014)
++++++++++++++++++

* Added: reports at the end of running all the major commands.
* Added: ``envs`` to specification for environment variable definitions.
* Added: ``command`` to specification for run command definition.
* Added: ``pull`` command to download all images required for the
specification.
* Added ``specification`` to specification for external specification links.

0.2.0 (25-02-2014)
++++++++++++++++++

* Added: supervisor config writing is now an option.
* Added: deconstruct command to remove a specification.

0.1.0 (25-02-2014)
++++++++++++++++++

* First release on PyPI.
