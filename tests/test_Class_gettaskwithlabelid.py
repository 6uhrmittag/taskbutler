#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `taskbutler` package."""

import pytest
import sys

from todoist.api import TodoistAPI
from taskbutler import taskbutler


class TestClassGetTaskWithLabelID:

    @pytest.fixture(scope='session')
    def API_BEFORE(self):
        testpath = sys.path[0] + '/'
        data = TodoistAPI(cache=testpath, token="todoist_testdata_before")
        return data

    @pytest.fixture(scope='session')
    def labelID(self):
        labelID = 2149853835
        return labelID

    @pytest.fixture(scope='session')
    def existingLabels(self):
        existingLabels = [
            2886409846,
            2886413088,
            2886413693,
            2886413793,
            2886415012,
            2886433224
        ]
        return existingLabels

    def test_Returns_wist_with_existing_label(self, labelID, API_BEFORE, existingLabels):
        taskbutler.api = API_BEFORE
        dings = taskbutler.gettaskwithlabelid(labelID)
        assert dings == existingLabels

    def test_Returns_empty_list_when_no_label_is_found(self, API_BEFORE, existingLabels):
        taskbutler.api = API_BEFORE
        dings = taskbutler.gettaskwithlabelid(11)
        assert dings == []

    @pytest.mark.skip(reason="TODO: Not implemented yet")
    def test_Raises_an_error_if_label_empty(self, API_BEFORE, existingLabels):
        taskbutler.api = API_BEFORE
        with pytest.raises(ValueError, match="not found"):
            taskbutler.gettaskwithlabelid("")
