#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `taskbutler` package."""

import pytest

from taskbutler import taskbutler


class TestClassCheckForUpdate:

    def test_returns_0_when_up_to_date(self):
        exit = taskbutler.checkforupdate("v.2.0.0", "https://api.github.com/repos/6uhrmittag/taskbutler/releases")
        if exit == 1:
            pytest.xfail("Version can be outdated or Github blocks connection")
        else:
            assert exit == 0

    def test_returns_1_when_NOT_up_to_date(self):
        exit = taskbutler.checkforupdate("v.1.0.0", "https://api.github.com/repos/6uhrmittag/taskbutler/releases")
        assert exit == 1

    def test_returns_1_when_URL_wrong(self):
        exit = taskbutler.checkforupdate("v.1.0.0", "https://doesntexist")
        assert exit == 1
