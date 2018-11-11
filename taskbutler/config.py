#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""static config for taskbutler."""

import os
from configparser import ConfigParser
import codecs


# configuration directories

class staticConfig():
    # directory names
    dir_app = '.taskbutler'
    dir_config = 'config'
    dir_templates = 'templates'
    dir_log = 'log'

    # file names
    filename_config = 'config.ini'
    filename_config_initial = 'config.ini.sample'
    filename_log = 'taskbutler.log'


class getConfigPaths():

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

    def file_config(self):
        return os.path.join(self.user(), staticConfig.dir_app, staticConfig.dir_config, staticConfig.filename_config)


def readConfig(configFile, Section, Item):
    config = ConfigParser()
    config.read_file(open(configFile, 'r', encoding='utf-8'))
    value = config.get(Section, Item)
    return value


def writeConfig(configFile, Section, Item, Value):
    config = ConfigParser()
    config.read_file(open(configFile, 'r', encoding='utf-8'))
    config.set(Section, Item, Value)
    with open(configFile, 'w') as writeFile:
        config.write(codecs.open(configFile, 'wb+', 'utf-8'))


class configTodoist():
    """Default Values"""

    def __init__(self):
        self.apikey = ''
        self.label_progress = 'progressbar'
        self.progress_seperator = '‣'
        self.progress_bar_0 = '⬜⬜⬜⬜⬜'
        self.progress_bar_20 = '⬛⬜⬜⬜⬜'
        self.progress_bar_40 = '⬛⬛⬜⬜⬜'
        self.progress_bar_60 = '⬛⬛⬛⬜⬜'
        self.progress_bar_80 = '⬛⬛⬛⬛⬜'
        self.progress_bar_100 = '⬛⬛⬛⬛⬛'

    def load(self):
        """Load from config File"""
        self.apikey = readConfig(getConfigPaths().file_config(), 'todoist', 'apikey')
        self.label_progress = readConfig(getConfigPaths().file_config(), 'todoist', 'apikey')
        self.progress_seperator = readConfig(getConfigPaths().file_config(), 'todoist', 'apikey')
        self.progress_bar_0 = readConfig(getConfigPaths().file_config(), 'todoist', 'apikey')
        self.progress_bar_20 = readConfig(getConfigPaths().file_config(), 'todoist', 'apikey')
        self.progress_bar_40 = readConfig(getConfigPaths().file_config(), 'todoist', 'apikey')
        self.progress_bar_60 = readConfig(getConfigPaths().file_config(), 'todoist', 'apikey')
        self.progress_bar_80 = readConfig(getConfigPaths().file_config(), 'todoist', 'apikey')
        self.progress_bar_100 = readConfig(getConfigPaths().file_config(), 'todoist', 'apikey')
