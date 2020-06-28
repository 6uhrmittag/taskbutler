#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `taskbutler` package."""

import pytest
import sys

from todoist.api import TodoistAPI
from taskbutler import taskbutler


class TestClassGetRawPriceFromGrocery:

    Titles = [
            ('banane - 3.0€', '3.0'),
            ('banane - 7.0€', '7.0'),
            ('banane - 8.66€', '8.66'),
            ('banane - 12.0€', '12.0'),
            ('banane - 9.1€', '9.1'),
             ]

    Task = [
            ('banane 3€', '3'),
            ('banane 6.7€', '6.7'),
            ('banane 5.0€', '5.0'),
            ('banane 1.11€', '1.11'),
             ]

    currency = [
            ('banane - 3€', '€', '3'),
            ('banane - 3$', '$', '3'),
             ]

    seperator = [
            ('banane - 3.0€', '-', '3.0'),
            ('banane % 7.0€', '%', '7.0'),
            ('banane 👻 8.66€', '👻', '8.66'),
            ('banane # 12.0€', '#', '12.0'),
            ('banane : 9.1€', ':', '9.1'),
             ]

    @pytest.mark.parametrize("titel, price", Titles)
    def test_Returns_getRawPriceFromGroceryTitle(self, titel, price):
        dings = taskbutler.getRawPriceFromGrocery(titel, '€', '-', isTitle=True)
        assert dings == float(price)

    @pytest.mark.parametrize("titel, price", Task)
    def test_Returns_getRawPriceFromGroceryTask(self, titel, price):
        dings = taskbutler.getRawPriceFromGrocery(titel, '€', '-', isTitle=False)
        assert dings == float(price)

    @pytest.mark.parametrize("titel, seperator, price", seperator)
    def test_Returns_getRawPriceFromGrocerySeperator(self, titel, seperator, price):
        dings = taskbutler.getRawPriceFromGrocery(titel, '€', seperator, isTitle=True)
        assert dings == float(price)