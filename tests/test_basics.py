#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from click.testing import CliRunner

from taskbutler import taskbutler
from taskbutler import cli

"""Tests for `taskbutler` package."""


@pytest.mark.second
@pytest.mark.serial
class TestCLI:

    def testCLIHelp(self):
        """Test the CLI."""
        runner = CliRunner()
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output

    # @pytest.mark.xfail
    def test_cli_main_basic(self, capsys):
        runner = CliRunner()
        result = runner.invoke(cli.main)
        # with capsys.disabled():
        #    print(result.output)
        assert 'Taskbutler - INFO - Read config from:' in result.output
        assert result.exit_code == 1


class TestModifyTitle:

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
    def test_get_task_title(self, title, seperator, additional):
        assert taskbutler.gettasktitle(title + seperator + additional, seperator) == title

    def test_add_url_to_task(self):
        assert taskbutler.addurltotask("google", "https://google1.com", "-") == 'https://google1.com (google) '
        assert taskbutler.addurltotask("google - X", "https://google3.com", "-") == 'https://google3.com (google) - X'
