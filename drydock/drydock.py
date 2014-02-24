from __future__ import print_function
from . import __version__
__doc__ = """DryDock v{}

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
configure a cluster of docker containers. DryDock will automatically setup a
reverse proxy, exposure of ports, and even persistent storage to allow for
easy future upgrading by simply rebuilding the DryDock specification!

For documentation go to http://dry-dock.readthedocs.org/
""".format(__version__)
import yaml
from . import construction
from .duster import MetaContainer
from docopt import docopt


def main():
    """Main entry point."""
    args = docopt(__doc__, version="DryDock v" + __version__)

    if args["construct"]:
        with open(args["<specification>"], 'r') as drydock:
            construction.construct(MetaContainer(**yaml.load(drydock.read())))

    elif args["prepare"]:
        construction.prepare()

    elif args["master"]:
        construction.drydock(
            args["--http"], args["--https"], args["--ssh"], args["<name>"])


if __name__ == "__main__":
    main()
