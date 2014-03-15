from __future__ import print_function
from . import __version__
__doc__ = """DryDock v{}

Usage:
    drydock construct <specification>
    drydock deconstruct <specification>
    drydock pull <specification>
    drydock start <specification>
    drydock supervise <specification>
    drydock stop <specification>
    drydock prepare [--ssl]
    drydock master <specification>
    drydock --help | --version

Options:
    -s --ssl                Generate SSL certificates.

    -h --help               Show this screen.
    -v --version            Show current version.

Commands:
    construct    Construct the given specification.
    deconstruct  Deconstruct the given specification.
    prepare      Prepare docker for constructing a drydock specification.
    master       Create a container that can run a drydock specification.

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
            construction.construct(
                MetaContainer(**yaml.load(drydock.read())))

    elif args["deconstruct"]:
        with open(args["<specification>"], 'r') as drydock:
            construction.deconstruct(
                MetaContainer(**yaml.load(drydock.read())))

    elif args["pull"]:
        with open(args["<specification>"], 'r') as drydock:
            construction.pull(
                MetaContainer(**yaml.load(drydock.read())))

    elif args["start"]:
        with open(args["<specification>"], 'r') as drydock:
            construction.start(
                MetaContainer(**yaml.load(drydock.read())))

    elif args["supervise"]:
        with open(args["<specification>"], 'r') as drydock:
            construction.supervise(
                MetaContainer(**yaml.load(drydock.read())))

    elif args["stop"]:
        with open(args["<specification>"], 'r') as drydock:
            construction.stop(
                MetaContainer(**yaml.load(drydock.read())))

    elif args["master"]:
        with open(args["<specification>"], 'r') as drydock:
            construction.master(
                MetaContainer(**yaml.load(drydock.read())),
                args["<specification>"])

    elif args["prepare"]:
        construction.prepare(args["--ssl"])


if __name__ == "__main__":
    main()
