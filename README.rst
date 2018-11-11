==========
Taskbutler
==========

Taskbutler enriches your Todoist tasks by adding progress bars, Office365 Files and Dropbox Paper papers directly to your tasks.

.. image:: https://travis-ci.org/6uhrmittag/taskbutler.svg?branch=feature-githubsync
    :target: https://travis-ci.org/6uhrmittag/taskbutler
    :alt: Travis

.. image:: https://www.codefactor.io/repository/github/6uhrmittag/taskbutler/badge/feature-githubsync
    :target: https://www.codefactor.io/repository/github/6uhrmittag/taskbutler/overview/feature-githubsync
    :alt: CodeFactor

.. image:: https://api.codeclimate.com/v1/badges/02c45c0604ad57ffc504/maintainability
    :target: https://codeclimate.com/github/6uhrmittag/taskbutler/maintainability
    :alt: Maintainability

.. image:: https://pyup.io/repos/github/6uhrmittag/taskbutler/shield.svg
    :target: https://pyup.io/repos/github/6uhrmittag/taskbutler/
    :alt: Updates

.. image:: https://readthedocs.org/projects/taskbutler/badge/?version=latest
    :target: https://taskbutler.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Features
========

-  **add progress bars to task-lists in Todoist (unicode,
   cross-plattform)**

   -  Example usage: Create a new task list "File taxes" in your
      "personal" Todoist project. Add the label "progressbar" to the top
      task and always get the status of your taxes at a glance.

    .. image:: /_static/win-web-demo-list.png

-  **add and link a Word/Office365 template to tasks** (with help of
   your Dropbox)

   -  Example usage: Setup a letter template in Microsoft Word once and
      save it. Once you add the label "letter" to your Todoist task, the
      template gets uploaded to your Dropbox and the task get liked to
      Microsoft Office365. Now, by clicking the task in Todoist,
      Microsoft Word online opens in your browser and you can start
      writing.

    .. image:: /_static/feature-office.gif

-  **add and link Dropbox Paper papers to tasks**

   -  Example usage: Tired of the missing task-note feature in Todoist?
      Add the label "paper" to a task. Now, with a click on the title,
      you'll get a new Dropbox Paper with all its features just for this
      task.

    .. image:: /_static/feature-paper.gif

Prerequisites and notes
=======================
**Taskbutler is not associated or connected with Todoist, Dropbox,
Github or Microsoft.**

1. You'll need a `Todoist <https://todoist.com>`_ premium account
2. The Dropbox Paper and Github features require a free account at
   Dropbox. The Microsoft Office365 feature requires a paid Office365
   subscription(or a free Microsoft Office 365 Education subscription).
3. Taskbutler is tested on Ubuntu
4. For optimal use, Taskbutler should run periodical on a
   server/computer to continuously update your tasks

*Even though I never experienced any data loss, it's nice to know
that*\ `Todoist provides a daily backup of your data. <https://support.todoist.com/hc/en-us/articles/115001799989>`_


Setup
=====

requirements
------------

- Ubuntu 16 and up
- tested with Python 3.5 and up

install
-------

To install the latest taskbutler in your home directory, run this commands in your terminal:
(Feel free to install it anywhere you want. Just adapt the path when using this readme.)


.. code-block:: console

    cd ~
    mkdir taskbutler && cd taskbutler
    sudo apt-get install python3
    python3 -m pip install --user --upgrade pip
    python3 -m venv venv
    pip install --upgrade pip
    ~/taskbutler/source venv/bin/activate
    pip install taskbutler


configuration
-------------

The configuration is stored in your home directory: `/home/$YourUsername/.taskbutler/config/config.ini`

Each feature can be disabled by leaving the corresponding labelname in
the config.ini emtpy. Each feature is configured in the config.ini.
Open, edit and save the file to configure Taskbutler.

If you used Taskbutler before and want to change a setting: **Remember
to stop Taskbutler before changing any setting and always update your
existing Todoist tasks manually according to your changes before
starting Taskbutler again.**

Taskbutler is not aware of your changes and will mix and mess up your
tasks. Changes can easily be tested by using a different/new labelname.

Setup Progress bars
^^^^^^^^^^^^^^^^^^^

Edit the config section in config.ini:

.. code:: ini

   [todoist]
   apikey =
   label_progress = progressbar
   progress_seperator=‣
   progress_bar_0=⬜⬜⬜⬜⬜
   progress_bar_20=⬛⬜⬜⬜⬜
   progress_bar_40=⬛⬛⬜⬜⬜
   progress_bar_60=⬛⬛⬛⬜⬜
   progress_bar_80=⬛⬛⬛⬛⬜
   progress_bar_100=⬛⬛⬛⬛⬛

Change progressbar symbols
""""""""""""""""""""""""""


The bar is implemented by adding 'unicode charaters'_ to the existing
text. e.g. ⬛⬛⬜⬜⬜ 33 %

.. code:: ini

   [todoist]
   progress_bar_0=⬜⬜⬜⬜⬜
   progress_bar_20=⬛⬜⬜⬜⬜
   progress_bar_40=⬛⬛⬜⬜⬜
   progress_bar_60=⬛⬛⬛⬜⬜
   progress_bar_80=⬛⬛⬛⬛⬜
   progress_bar_100=⬛⬛⬛⬛⬛

.. _unicode charaters: http://jrgraphix.net/r/Unicode/2600-26FF


To change the bar to e.g. empty/full bullets, just overwrite the
characters with other characters ''⚫⚫⚫⚪⚪''.

Change progressbar seperator
""""""""""""""""""""""""""""
To separate the task-text from the progressbar, a rare unicode character
is used. To change the separator just change the line
''progress_seperator=‣'' in the ''config.ini'' file.

.. code:: ini

   [todoist]
   progress_seperator=‣

Just replace the existing character with the character of your choice.
Remember to rename the separator manually in Todoist before running
Taskbutler again!

Edit progressbar label
""""""""""""""""""""""

The bar added to every task with the label ''progressbar''. The
label-name can be changed in the ''config.ini'' file:
''label_progress=progressbar'' To change the labelname after the "=".
Remember to rename the label in Todoist when renaming labels!

Setup Dropbox features
^^^^^^^^^^^^^^^^^^^^^^


To use any Dropbox feature you need to create a Dropbox API token. You
need to create an Dropbox app for that. Don't worry, you only need to
setup it once and it is only accessible for you.

Get a API key for your Dropbox(by creating a Dropbox app):

1. Go to `https://www.dropbox.com/developers/apps/create <https://www.dropbox.com/developers/apps/create>`_
2. Select *Dropbox API*
3. Select *Full Dropbox- Access to all files and folders in a user's Dropbox.*
4. Give it a name (doesn't matter)
5. Click *Create app*
6. On the app settings page click *Generated access token* and copy
   the token




Setup Office365 Sync
^^^^^^^^^^^^^^^^^^^^

You need:

-  an Dropbox account
-  an Microsoft Office365/office.com account
-  an .docx template you want to add by the label

Pre-tasks
"""""""""


-  create a new folder in `your Dropbox <https://www.dropbox.com/h>`_. All files will be saved here
-  connect Microsoft Office Online to 'your
   Dropbox `<https://www.dropbox.com/account/connected_apps>`__

Edit the config section in config.ini:

.. code:: ini

   [dropbox]
   apikey =

   [dropboxoffice]
   labelname = letter
   templatefile = ./templates/
   folder=todoist
   dropbox_prepart_files = https://www.dropbox.com/ow/msft/edit/home/

-  apikey: add the Dropbox API key you created above
-  labelame: add the Todoist label you want to use for this feature
-  templatefile: add the path to your .docx file you want to add to your
   tasks (Linux style, full or relative from /tasbutler)
-  folder: add the Dropbox folder you created above
-  dropbox_prepart_files: don't change. Needed to create the Office365
   direct link

Setup Dropbox Paper
^^^^^^^^^^^^^^^^^^^


Pre-tasks
^^^^^^^^^


-  create a new folder in your `Dropbox Paper <https://paper.dropbox.com/folders>`_. All papers will be
   saved here
-  Create an empty paper in this folder(Taskbutler only recognises
   folders once a paper is placed in it)
-  Edit your config.ini:

Edit the config section in config.ini:

.. code:: ini

   [dropbox]
   apikey =

   [dropboxpaper]
   todoistfolderid =
   url = https://paper.dropbox.com/doc/
   labelname = paper
   foldername = todoist
   sharing = false


-  apikey: add the Dropbox API key you created above
-  todoistfolderid: don't change. Will get set automatically by
   Taskbutler. ID of the Dropbox Paper folder you created above
-  url: don't change. Needed to create the Dropbox Paper direct link
-  labelame: add the Todoist label you want to use for this feature
-  foldername: add the Dropbox Paper folder you created above
-  sharing: don't change. Sets the created papers to "private only" (so
   only you, once logged into Dropbox, will be able to access it)

Start Taskbutler
^^^^^^^^^^^^^^^^

.. code:: console

    source ~/taskbutler/venv/bin/activate
    taskbutler


Continuous progress-update
^^^^^^^^^^^^^^^^^^^^^^^^^^

To continuously update your tasks run Taskbutler periodical on a server
or your computer

Ubuntu Server
"""""""""""""

**TODO: This section is not complete yet.**

run programm every 20Min via crontab (see `crontab.guru <https://crontab.guru/>`_ for setting
time):

.. code:: bash

    #! /bin/bash
    # add the full path to your venv at PATH_VENV_TASKBUTLER
    # ~/taskbutler/
    cd PATH_VENV_TASKBUTLER

    #activate taskbutler venv
    source bin/activate

    # run taskbutler
    taskbutler


1. save the script above on your computer
2. adjust the PATH_VENV_TASKBUTLER
3. remember the full path to the saved scriped
4. type: :code:`crontab -e`
5. add a line: :code:`*/20 * * * * ADD_THE_REMEMBERED_PATH_HERE`


Computer(Win/Mac/Linux)
"""""""""""""""""""""""

Taskbutler doesn't need to run on a server. It is also possible to run
Taskbutler on your running computer. Just start Taskbutler manually or
add it to your scheduled tasks.

Updates
-------


Taskbutler checks for updates by checking the 'releases page'_ and
leaves a message in the console.

To update:

-  See releasenotes at `releases page <https://github.com/6uhrmittag/taskbutler/releases>`_ and check for compatibility.
-  Backup your current configuration/setup-folder
-  Download release from 'releases page'_ and overwrite files or "git
   pull origin" when you cloned this repository
-  Check and set all configurations. Use a different label name for
   testing (set ''label_progress'' and create a task with the test
   label)


Logging
-------

If a logfile is specified, Taskbutler logs into this file. If not,
Taskbutler logs to the console only.

Development
===========


To activate dev-mode add to ini file:

.. code:: ini

   [config]
   devmode = true

Devmode doesn't submit changes to Todoist, Dropbox or Github. Set the
logging level to DEBUG to get all messages.

.. code:: ini

   [log]
   loglevel=DEBUG
   logfile = ./todoist.log

Built With
==========


- `Doist/todoist-python <https://github.com/Doist/todoist-python>`_ - The official Todoist Python API library
- `dropbox/dropbox-sdk-python <https://github.com/dropbox/dropbox-sdk-python>`_ - The official Python SDK for Dropbox
   API v2
- `PyGithub python sdk <https://github.com/PyGithub/PyGithub>`_ - Unofficial Python SDK for Github API
- `Cookiecutter template for a Python package <https://github.com/audreyr/cookiecutter-pypackage>`_

Contributing


Please open a issue in the 'Github issue tracker `<https://github.com/6uhrmittag/taskbutler/issues>`_.


About Author
============

**Marvin Heimbrodt** - `github.com/6uhrmittag <https://github.com/6uhrmittag/>`_
