"""
DryDock can automatically provision a cluster of docker containers based on
a simple configuration file.
"""
from __future__ import print_function
import json
import os
import sys
from .construction import construct
from .duster import parse


def main():
    try:
        with open('drydock.json') as drydock:
            spec = parse(json.load(drydock))
            construct(spec)
    except IOError:
        print("ERROR: Cannot find 'drydock.json' config in ", os.getcwd())
        sys.exit(1)


if __name__ == "__main__":
    main()