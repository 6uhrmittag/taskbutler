#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `taskbutler` package."""

import pytest
import sys

from todoist.api import TodoistAPI
from taskbutler import taskbutler

@pytest.fixture(scope='session')
def API_BEFORE():
    testpath = sys.path[0] + '/'
    data = TodoistAPI(cache=testpath, token="todoist_testdata_before")
    return data


@pytest.fixture(scope='session')
def labelID():
    labelID = 2149853835
    return labelID


@pytest.fixture(scope='session')
def existingLabels():
    existingLabels = [
        2886409846,
        2886413088,
        2886413693,
        2886413793,
        2886415012,
        2886433224
    ]
    return existingLabels


def test_Returns_wist_with_existing_label(labelID, API_BEFORE, existingLabels):
    dings = taskbutler.gettaskwithlabelid(labelID, API_BEFORE)
    assert dings == existingLabels

def test_Returns_empty_list_when_no_label_is_found(API_BEFORE, existingLabels):
    dings = taskbutler.gettaskwithlabelid(11, API_BEFORE)
    assert dings == []

@pytest.mark.skip(reason="TODO: Not implemented yet")
def test_Raises_an_error_if_label_empty(API_BEFORE, existingLabels):
    with pytest.raises(ValueError, match="not found"):
        taskbutler.gettaskwithlabelid("", API_BEFORE)