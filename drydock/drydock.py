from __future__ import print_function
__doc__ = """DryDock

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

DryDock can convert a simple configuration file into a Dockerfile
(and accompanying configs) that when built will run a cluster of docker
containers. The end product will automatically setup a reverse proxy, exposure
of ports, and even persistent storage to allow for easy future upgrading by
simply rebuilding the DryDock specification!

For documentation go to http://dry-dock.readthedocs.org/
"""
import yaml
from . import construction
from .duster import MetaContainer
from docopt import docopt
from . import __version__


def main():
    """Main entry point."""
    args = docopt(__doc__, version="DryDock v" + __version__)

    if args["construct"]:
        with open(args["specification"], 'r') as drydock:
            construction.construct(MetaContainer(**yaml.load(drydock.read())))

    elif args["prepare"]:
        construction.prepare()

    elif args["master"]:
        construction.drydock(
            args["--http"], args["--https"], args["--ssh"], args["name"])


if __name__ == "__main__":
    main()
