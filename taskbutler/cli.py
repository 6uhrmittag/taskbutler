# -*- coding: utf-8 -*-

"""Console script for taskbutler."""
import click
from . import taskbutler


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """This script showcases different terminal UI helpers in Click."""
    if ctx.invoked_subcommand is None:
        main()
    else:
        pass


@cli.command()
def main(args=None):
    """Console script for taskbutler."""
    taskbutler.main()
    return 0


if __name__ == "__main__":
    cli()
