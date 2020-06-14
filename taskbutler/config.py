#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""static config for taskbutler."""

import os


# configuration directories
class staticConfig:
    # directory names
    dir_app = '.taskbutler'
    dir_config = 'config'
    dir_templates = 'templates'
    dir_log = 'log'
    dir_cronjobs = 'cronjobs'

    # file names
    filename_config = 'config.ini'
    filename_config_initial = 'config.ini.sample'
    filename_log = 'taskbutler.log'


class getConfigPaths:

    def user(self):
        return os.path.expanduser('~')

    def app(self):
        return os.path.join(self.user(), staticConfig.dir_app)

    def config(self):
        return os.path.join(self.user(), staticConfig.dir_app, staticConfig.dir_config)

    def log(self):
        return os.path.join(self.user(), staticConfig.dir_app, staticConfig.dir_log)

    def templates(self):
        return os.path.join(self.user(), staticConfig.dir_app, staticConfig.dir_templates)

    def cronjobs(self):
        return os.path.join(self.user(), staticConfig.dir_app, staticConfig.dir_cronjobs)

    def file_config(self):
        return os.path.join(self.user(), staticConfig.dir_app, staticConfig.dir_config, staticConfig.filename_config)