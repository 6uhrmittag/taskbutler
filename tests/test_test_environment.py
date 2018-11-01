#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import os.path
from os import path


"""Tests environment to make sure the test setup works"""

def test_path_to_tests_directory(capsys):
    with capsys.disabled():
        print(sys.path[0])

def test_path_to_tests_directory_baskslashed(capsys):
    with capsys.disabled():
        print(sys.path[0] + '/')

def test_path_to_todoistJSON_like_API(capsys):
    with capsys.disabled():
        print(os.path.expanduser('todoist_testdata_before.json'))
        print(os.path.expanduser(sys.path[0] + '/' )+ 'todoist_testdata_before.json')
    assert path.exists(os.path.expanduser('todoist_testdata_before.json')) is True
