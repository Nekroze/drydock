"""
DryDock can automatically provision a cluster of docker containers based on
a simple configuration file.
"""
from __future__ import print_function
import yaml
import os
import sys
from .construction import construct
from .duster import MetaContainer


def main():
    try:
        with open('drydock.yaml') as drydock:
            spec = MetaContainer(**yaml.load(drydock.read()))
            return spec
    except IOError:
        print("ERROR: Cannot find 'drydock.yaml' config in ", os.getcwd())
        sys.exit(1)


if __name__ == "__main__":
    main()