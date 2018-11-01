#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `taskbutler` package."""

import pytest
import sys

from todoist.api import TodoistAPI
from taskbutler import taskbutler


@pytest.fixture(scope='session')
def API_BEFORE():
    testpath = sys.path[0] +'\\'
    data = TodoistAPI(cache=testpath, token="todoist_testdata_before")
    return data



def test_It_Should_Find_A_Given_Label(API_BEFORE):
    success = taskbutler.getlabelid("progressbar", API_BEFORE)
    assert success == 2149853835

def test_It_Should_Raise_An_Error_If_Label_Is_Empty(API_BEFORE):
    with pytest.raises(ValueError, match="not found"):
        taskbutler.getlabelid("", API_BEFORE)

def test_It_Should_Raise_An_Error_If_Noting_Is_Found(API_BEFORE):
    with pytest.raises(ValueError, match="not found"):
        taskbutler.getlabelid("NON_EXISTING", API_BEFORE)
