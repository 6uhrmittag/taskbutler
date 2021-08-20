#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', 'todoist-python', 'PyGithub', 'requests', 'dropbox']

# TODO: mark python3 as required
setup(
    author="Marvin Heimbrodt",
    author_email='marvin@6uhrmittag.de',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Taskbutler enriches your Todoist tasks by adding progress bars, Office365 Files and Dropbox Paper papers directly to your tasks.",
    entry_points={
        'console_scripts': [
            'taskbutler=taskbutler.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='taskbutler',
    name='taskbutler',
    packages=find_packages(include=['taskbutler']),
    test_suite='tests',
    url='https://github.com/6uhrmittag/taskbutler',
    version='2.2.5',
    zip_safe=False,
)
