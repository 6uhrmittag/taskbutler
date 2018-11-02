#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import os.path
from os import path

import taskbutler.config as config
import shutil

"""Tests environment to make sure the test setup works"""


class TestEnvPaths:

    def test_print_path_to_tests_directory(self, capsys):
        with capsys.disabled():
            print(sys.path[0])

    def test_path_to_todoistJSON_like_API_exists(self, capsys):
        assert path.exists(os.path.expanduser(os.path.expanduser(sys.path[0] + '/') + 'todoist_testdata_before.json')) is True


class TestConfigVariables:

    def test_test_static_config_variables_exist(self, capsys):
        assert config.staticConfig.dir_app == '.taskbutler'
        assert config.staticConfig.dir_config == 'config'
        assert config.staticConfig.dir_templates == 'templates'
        assert config.staticConfig.dir_log == 'log'

        assert config.staticConfig.filename_config == 'config.ini'
        assert config.staticConfig.filename_config_initial == 'config.ini.sample'
        assert config.staticConfig.filename_log == 'taskbutler.log'

    def test_print_config_paths(self, capsys):
        # To make debugging easier
        with capsys.disabled():
            print('paths in this env: ', config.getConfigPaths().user())
            print('paths in this env: ', config.getConfigPaths().app())
            print('paths in this env: ', config.getConfigPaths().config())
            print('paths in this env: ', config.getConfigPaths().config())
            print('paths in this env: ', config.getConfigPaths().log())
            print('paths in this env: ', config.getConfigPaths().templates())
            print('paths in this env: ', config.getConfigPaths().file_config())

            # Make sure the test reaches the config.ini.sample
            print('paths in this env: ', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'taskbutler', config.staticConfig.filename_config_initial))


class TestCreateConfigPaths:

    def test_create_config_path(self):
        # create config
        if not os.path.exists(config.getConfigPaths().app()):
            os.mkdir(config.getConfigPaths().app(), 700)

        if os.path.exists(config.getConfigPaths().app()) and not os.path.exists(config.getConfigPaths().config()):
            os.mkdir(config.getConfigPaths().config(), 700)

        assert os.path.exists(config.getConfigPaths().app()) is True
        assert os.path.exists(config.getConfigPaths().config()) is True

    def test_create_initial_config(self):
        # create initial config
        if not os.path.exists(config.getConfigPaths().file_config()):
            shutil.copy(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'taskbutler', config.staticConfig.filename_config_initial),
                        config.getConfigPaths().file_config())

        assert os.path.exists(config.getConfigPaths().file_config()) is True

    def test_create_template_paths(self):
        # create templates
        if os.path.exists(config.getConfigPaths().app()) and not os.path.exists(config.getConfigPaths().templates()):
            os.mkdir(config.getConfigPaths().templates(), 700)

        assert os.path.exists(config.getConfigPaths().templates()) is True

    def test_create_log_paths(self):
        # create log
        if os.path.exists(config.getConfigPaths().app()) and not os.path.exists(config.getConfigPaths().log()):
            os.mkdir(config.getConfigPaths().log(), 700)

        assert os.path.exists(config.getConfigPaths().log()) is True
