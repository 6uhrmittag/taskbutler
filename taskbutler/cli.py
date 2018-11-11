# -*- coding: utf-8 -*-

"""Console script for taskbutler."""
import sys
import click
from . import taskbutler
from codecs import open
from configparser import ConfigParser

# import static config
from .config import staticConfig, getConfigPaths


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """This script showcases different terminal UI helpers in Click."""
    if ctx.invoked_subcommand is None:
        main()
    else:
        pass


@click.group()
def config():
    """Modify options"""
    pass


@config.command()
def TodoistKey():
    print("test")


@cli.command()
def main(args=None):
    """Console script for taskbutler."""
    taskbutler.main()
    return 0


@cli.command()
@click.option('--TodoistApiKey', prompt='Type your Todoist API Key: ', help='Your Todoist Api Key')
def setConfig(TodoistApiKey):
    """Add or change your Todoist API key"""

if __name__ == "__main__":
    cli()
