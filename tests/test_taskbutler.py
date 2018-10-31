#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `taskbutler` package."""

import pytest

from click.testing import CliRunner

from taskbutler import taskbutler
from taskbutler import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 1
    # assert 'taskbutler.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


@pytest.mark.parametrize(
    ('title', 'seperator', 'additional'), [
        ('dings', '*', 'dings'),
        ('dings', '‣', 'random'),
        ('dings', '\'', 'random'),
        ('dings', '%', 'ÄÄ*Ä:;;?=)(/_:'),
        ('dings', 'ÜÄ*', 'ÄÄ*Ä:;;?=)(/_:'),
        ('random', '', ''),
    ]
)
def test_gettasktitle(title, seperator, additional):
    assert taskbutler.gettasktitle(title + seperator + additional, seperator) == title

def test_addurltotask():
    assert taskbutler.addurltotask("google", "https://google1.com", "-") == 'https://google1.com (google) '
    assert taskbutler.addurltotask("google - X", "https://google3.com", "-") == 'https://google3.com (google) - X'

def test_taskbutler_basic(capsys):
    runner = CliRunner()
    result = runner.invoke(cli.main)
    # with capsys.disabled():
    #    print(result.output)
    assert 'Taskbutler - INFO - Read config from: config.ini' in result.output
