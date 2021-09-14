==========
Taskbutler
==========

Taskbutler enriches your Todoist tasks by adding progress bars, Office365 Files and Dropbox Paper papers directly to your tasks.

.. image:: https://github.com/6uhrmittag/taskbutler/actions/workflows/release.yml/badge.svg
    :target: https://github.com/6uhrmittag/taskbutler/actions/workflows/release.yml
    :alt: GithubActions

.. image:: https://www.codefactor.io/repository/github/6uhrmittag/taskbutler/badge/master
    :target: https://www.codefactor.io/repository/github/6uhrmittag/taskbutler/overview/master
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
   cross-platform)**

   -  Create a new task list and add the label "progressbar". Now you always know the progress without scrolling to your entire list.

    .. image:: /_static/win-web-demo-list.png

-  **add and link a Word/Office365 template to tasks** (with help of
   your Dropbox)

   -  Upload your favorite Word template by adding a label to your Todoist task. Taskbutler uploads the template to your Dropbox and the task get liked to
      Microsoft Office365. Now, by clicking the task in Todoist,
      Microsoft Word online opens in your browser and you can start
      writing.

    .. image:: /_static/feature-office.gif

-  **add and link Dropbox Paper papers to tasks**

   -  Tired of the missing task-note feature in Todoist?
      Add the label "paper" to a task. Now, with a click on the title,
      you'll get a new Dropbox Paper with all its features just for this
      task.

    .. image:: /_static/feature-paper.gif

-  **calculate total sums of grocery lists or financial planning**

   -  Want to know how much a list with $/€ values will cost you ?
      Add the label "grocery" to a list of task and taskbutler will calculate the total of all items in the list.
      It also works for a list of lists! Now you can e.g. plan how much money you'll need for each week of a month and the total of the month.

    .. image:: /_static/feature_grocery.gif

-  **automatically expand links to Jira tasks**

   -  Add links to Atlassian Jira tasks, and have them automatically converted to include the ticket number and description in the task.


Prerequisites and notes
=======================
**Taskbutler is not associated or connected with Todoist, Dropbox,
Github, Microsoft, or Atlassian.**

1. You'll need a `Todoist <https://todoist.com>`_ premium account
2. The various third-party connections (Dropbox Paper, Github, Office365, Jira) require corresponding accounts and API connections.
   For Dropbox Paper and Github those accounts are free.
   The Microsoft Office365 and Atlassian Jira features require paid subscriptions of the respective solution.
   *All of these are optional and not required to use the other features of taskbutler!*
3. Taskbutler is tested on Ubuntu and Mac OS
4. For optimal use, Taskbutler should run periodically on a server/computer to continuously update your tasks

*Even though I never experienced any data loss, it's nice to know
that* \ `Todoist provides a daily backup of your data. <https://support.todoist.com/hc/en-us/articles/115001799989>`_


Setup
=====

requirements
------------

- Ubuntu 16 and up or Mac OS
- Tested with Python 3.6 and up

install
-------

To install the latest Taskbutler in your home directory, run these commands in your terminal:

.. code-block:: console

    pip install taskbutler --user
    # To start taskbutler without full path:
    echo 'PATH="$PATH:$HOME/.local/bin/"' >> ~/.bash_profile


Configuration
-------------

The configuration is stored in your home directory: `/home/$YourUsername/.taskbutler/config/config.ini`.

Each feature can be disabled by leaving the corresponding labelname in
the config.ini empty. Each feature is configured in the config.ini.
Open, edit and save the file to configure Taskbutler.

If you used Taskbutler before and want to change a setting: **Remember
to stop Taskbutler before changing any setting and always update your
existing Todoist tasks manually according to your changes before
starting Taskbutler again.**

Taskbutler is not aware of your changes and will mix and mess up your
tasks. Changes can easily be tested by using a different labelname.

Setup Todoist access
^^^^^^^^^^^^^^^^^^^^

Taskbutler needs access to your Todoist account. This is done via an API key, you'll need to create.
This key is like a password - don't share it!

1. Login to Todoist and got to settings -> Integrations (https://todoist.com/prefs/integrations)
2. Scroll down to "API-Token" and copy the token
3. paste the token into the config.ini and save:

.. code:: ini

   [todoist]
   apikey = PUT_TOKEN_HERE

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


The bar is implemented by adding `unicode charaters`_ to the existing
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


To change the bar to bullets, just overwrite the
characters with other characters ''⚫⚫⚫⚪⚪''.

Change progressbar seperator
""""""""""""""""""""""""""""
To separate the task-text from the progressbar, a rare unicode character
is used. Just replace the seperator in the ''config.ini'' file.

.. code:: ini

   [todoist]
   progress_seperator=‣

Remember to rename the separator manually in Todoist before running
Taskbutler again!

Edit progressbar label
""""""""""""""""""""""

The bar added to every task with the label ''progressbar''. The
label-name can be changed in the ''config.ini'' file:

.. code:: ini

   label_progress=progressbar

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

Setup Grocery list/Cost calulator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Edit the config section in config.ini:

.. code:: ini

   [todoist]
   label_grocery = grocery
   grocery_seperator = 💰
   grocery_currency = €


-  label_grocery: add the Todoist label you want to use for this feature
-  grocery_seperator: the character that separates the task name and calculated value
-  grocery_currency: your currency. Tested with $ and € - but it should work with all symbols


Setup Atlassian Jira sync
^^^^^^^^^^^^^^^^^^^^^^^^^

Edit the `jira` section in the config.ini file:

.. code:: ini

   [jira]
   link_expansion_enabled = true
   todoist_project_include = Project 1, Project 2/Subproject B
   todoist_project_exclude = Project 1/Subproject A, Project 4

Of these, `todoist_project_include` and `todoist_project_exclude` are optional.
If both are absent, all tasks in all projects are processed.
If include is present, only the tasks from the listed projects are used.
With exclude present, all tasks from the given projects are excluded.
Both lists are comma-separated project names with the slash used to specify sub-projects.

Additionally, for each Jira site for which you want to use this feature, you need to create a separate section with the required configuration:

.. code:: ini

   [jira.mysite]
   url = https://mysite.atlassian.net
   username = foo@example.com
   password = JIRA_API_TOKEN_HERE
   prefix = BG,TES

The password must be an API token, not your actual account password (see `Manage API tokens for your Atlassian account <https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/>`_).

The `prefix` key is an optional list of ticket prefixes that should be auto-expanded. In the example above, if you create a Todoist task simply called "BG-123", it will be assumed to refer to a Jira ticket in the `mysite` project and expanded.


Start Taskbutler
^^^^^^^^^^^^^^^^

Make sure you added the Python default path to your PATH via: `echo 'PATH="$PATH:$HOME/.local/bin/"' >> ~/.bash_profile`


.. code:: console

    # taskbutler now starts by simply typing:
    taskbutler


Continuous progress-update
^^^^^^^^^^^^^^^^^^^^^^^^^^

To continuously update your tasks run Taskbutler periodical on a internet connected server
or your computer

Ubuntu Server
"""""""""""""

To run taskbutler every 20Min via crontab (see `crontab.guru <https://crontab.guru/>`_ for setting
time):

1. type: :code:`crontab -e`
2. add the line: :code:`*/20 * * * * $HOME/.local/bin/taskbutler`
3. make sure to leave the last line in crontab empty or add a line with just a `#` at the end!(crontab needs this to work.)


Taskbutler will log to: `/home/$YourUsername/.taskbutler/log/todoist.log`

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
-  run :code:`pip install taskbutler --user --upgrade --upgrade-strategy eager` to update
-  Check and set all configurations. Use a different label name for
   testing (set ''label_progress'' and create a task with the test
   label)


Logging
-------

Taskbutler logs to `/home/$YourUsername/.taskbutler/logs`
The filename can be changed in the config.ini. You can also set the logging level. Default is `INFO`, `DEBUG` outputs logs of details.

.. code:: ini

    [log]
    loglevel= INFO
    logfile = todoist.log



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
- `dropbox/dropbox-sdk-python <https://github.com/dropbox/dropbox-sdk-python>`_ - The official Python SDK for Dropbox API v2
- `PyGithub python sdk <https://github.com/PyGithub/PyGithub>`_ - Unofficial Python SDK for Github API
- `Cookiecutter template for a Python package <https://github.com/audreyr/cookiecutter-pypackage>`_

Contributing


Please open a issue in the 'Github issue tracker `<https://github.com/6uhrmittag/taskbutler/issues>`_.


About Author
============

**Marvin Heimbrodt** - `github.com/6uhrmittag <https://github.com/6uhrmittag/>`_ | `twitter.com/6uhrmittag <https://twitter.com/6uhrmittag>`_

.. image:: https://www.ko-fi.com/img/githubbutton_sm.svg
    :target: https://ko-fi.com/K3K01P66S
    :alt: Donate Coffein via Ko-fi
