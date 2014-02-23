from __future__ import print_function
__doc__ = """DryDock

Usage:
    drydock [options] <specification>
    drydock (-h | --help)
    drydock (-v | --version)

Options:
    -o PATH --output PATH   Output path. [default: .]
    -h --help               Show this screen.
    -v --version            Show current version.

Dry Dock can convert a simple configuration file into a Dockerfile and
accompanying files that when built will run a cluster of docker containers
that will automatically setup with reverse proxying, exposure of ports and
even persistent storage to allow for easy future upgrading by simply
rebuilding the DryDock Dockerfile!
"""
import yaml
import os
import sys
from .construction import construct
from .duster import MetaContainer
from docopt import docopt
from . import __version__


def main():
    """Main entry point."""
    args = docopt(__doc__, version="DryDock v" + __version__)

    try:
        with open(args["specification"]) as drydock:
            spec = MetaContainer(**yaml.load(drydock.read()))
            construct(spec, args["--output"])
    except IOError:
        print("ERROR: Cannot find '{}' config in ".format(
            args["specification"]), args["--output"])
        sys.exit(1)


if __name__ == "__main__":
    main()
