# -*- coding: utf-8 -*-

"""Console script for taskbutler."""
import sys
import click
from . import taskbutler

@click.command()
def main(args=None):
    """Console script for taskbutler."""
    taskbutler.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
