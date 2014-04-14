from __future__ import print_function
from . import __version__
__doc__ = """DryDock v{}

Usage:
    drydock construct [options] <specification>
    drydock deconstruct <specification>
    drydock pull <specification>
    drydock start [options] <specification>
    drydock supervise [options] <specification>
    drydock stop <specification>
    drydock prepare [options]
    drydock master [options] <specification>
    drydock --help | --version

Options:
    -n --dns=<IP>           External dns server to use. [default: 8.8.8.8]
    -d --docker=<IFACE>     Docker  network interface. [default: docker0]
    -l --lan=<IFACE>        Local area network interface. [default: eth0]
    -g --gate=<INT>         Position of network gateway. [default: 1]

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
from .templates import prepare_networking


def main():
    """Main entry point."""
    args = docopt(__doc__, version="DryDock v" + __version__)

    if args["construct"]:
        prepare_networking(args["--lan"], args["--docker"], args["--gate"],
                           args["--dns"])
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
        prepare_networking(args["--lan"], args["--docker"], args["--gate"],
                           args["--dns"])
        with open(args["<specification>"], 'r') as drydock:
            construction.start(
                MetaContainer(**yaml.load(drydock.read())))

    elif args["supervise"]:
        prepare_networking(args["--lan"], args["--docker"], args["--gate"],
                           args["--dns"])
        with open(args["<specification>"], 'r') as drydock:
            construction.supervise(
                MetaContainer(**yaml.load(drydock.read())))

    elif args["stop"]:
        with open(args["<specification>"], 'r') as drydock:
            construction.stop(
                MetaContainer(**yaml.load(drydock.read())))

    elif args["master"]:
        prepare_networking(args["--lan"], args["--docker"], args["--gate"],
                           args["--dns"])
        with open(args["<specification>"], 'r') as drydock:
            construction.master(
                MetaContainer(**yaml.load(drydock.read())),
                args["<specification>"])

    elif args["prepare"]:
        prepare_networking(args["--lan"], args["--docker"], args["--gate"],
                           args["--dns"])
        construction.prepare(args["--ssl"])


if __name__ == "__main__":
    main()
