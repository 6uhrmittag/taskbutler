# todoist-progressbar

Adds visual progressbars to tasks and lists with subtasks

![Demo iOS](docs/images/win-web-demo-list.PNG)

[![Maintainability](https://api.codeclimate.com/v1/badges/63b8c36a47b407aa99aa/maintainability)](https://codeclimate.com/github/6uhrmittag/todoist-progressbar/maintainability)
[![CodeFactor](https://www.codefactor.io/repository/github/6uhrmittag/todoist-progressbar/badge/feature-dropboxpaper)](https://www.codefactor.io/repository/github/6uhrmittag/todoist-progressbar/overview/feature-dropboxpaper)

## Features

- uses unicode symbols for cross-platform support
- adds progressbars lists, sub-lists and individual tasks

## Prerequisites and notes

1. You'll need a [Todoist](https://todoist.com) premium account
2. The script is tested on Ubuntu
3. For optimal use this programm should run periodical on a server/computer to continuously update your tasks

*Even though I never experienced any data loss, it's nice to know that [Todoist provides a daily backup of your data.](https://support.todoist.com/hc/en-us/articles/115001799989)*

## Setup

### installing requirements

- `sudo apt-get install python3-pip`
- `git clone git@github.com:6uhrmittag/todoist-progress.git`
- `cd todoist-progress`
- `sudo pip3 install -r requirements.txt`
- `echo -e "[config]\napikey=YOURAPIKEY-WITHOUTH-ANY-QUOTES\nlabel_progress=trackprogress" >> config.ini`
- add a label named `trackprogress` to each list/task you want to track (only to the "top" task in the list)

## usage

- `cd todoist-progress/`
- `python3 todoist_progress.py`

## Continuous progress-update

This program updates existing tasks without creating new once. It used the official sync-api and shouldn't cause any
trouble while syncing.
To continuously update your tasks run this program periodical on a server/computer

### Ubuntu

run programm every 20Min via crontab
(see [crontab.guru](https://crontab.guru/) for setting time)

1. `sudo find / -name todoist_progress.py`
2. copy path without "todoist_progress.py" (e.g. `/home/USERNAME/todoisttest/todoist-progress/todoist-progress/`)
3. `crontab -e`
4. add: `*/20  *  * * * cd "INSERT-COPIED-PATH" && /usr/bin/python3 todoist_progress.py`

## Customisation

Most if the settings are customizable. Remember to **stop the program before changing any setting!**
Before starting the program again, change your todoist tasks manually!
Otherwise your task info will get mixed and messy.

### Edit progressbar symbols

The bar is implemented by adding [unicode charaters](http://jrgraphix.net/r/Unicode/2600-26FF) to the existing text.
e.g.  ⬛⬛⬜⬜⬜ 33 %
The characters are configurable in the `config.ini` file

```
[todoist]
progress_bar_0=⬜⬜⬜⬜⬜
progress_bar_20=⬛⬜⬜⬜⬜
progress_bar_40=⬛⬛⬜⬜⬜
progress_bar_60=⬛⬛⬛⬜⬜
progress_bar_80=⬛⬛⬛⬛⬜
progress_bar_100=⬛⬛⬛⬛⬛
```

To change the bar to e.g. empty/full bullets, just overwrite the characters with other charaters `⚫⚫⚫⚪⚪`.

### Edit progressbar seperator

The bar added to every task. To seperate the task-text from the progressbar a rare unicode charater is used.
To change the seperator just change the line `progress_seperator=‣` in the `config.ini` file.
Just replace the existing charater with your choice. Remember to rename the seperator manually in todoist before running the programm again!

### Edit progressbar label

The bar added to every task with the label `trackprogress`.
The label-name can be changed in the `config.ini` file:
`label_progress=trackprogress`
To change the labelname after the "=".
Remember to rename the label in todoist when renaming labels!

## Updates

The script checks for updates by checking the [releases page](https://github.com/6uhrmittag/todoist-progressbar/releases)
and leaves a message in the console.

To update:

- See releasenotes at [releases page](https://github.com/6uhrmittag/todoist-progressbar/releases)
and check for compatibility.
- Backup your current configuration/setup-folder
- Download release from [releases page](https://github.com/6uhrmittag/todoist-progressbar/releases)
and overwrite files or "git pull origin" when you cloned this repository
- Check and set all configurations. Use a different label name for testing (set `label_progress`
and create a task with the test label)

## Development

To activate dev-mode add to ini file:

````ini
[config]
devmode = true
````

Devmode doesn't submit changes to Todoist. **It will change dropbox files** (since messing up Todoist data is way more annoying)!

## Built With

* [Doist/todoist-python](https://github.com/Doist/todoist-python) - The official Todoist Python API library
* [dropbox/dropbox-sdk-python](https://github.com/dropbox/dropbox-sdk-python) - The official Python SDK for Dropbox API v2

## Contributing

Please leave a issue in the [Github issue tracker](https://github.com/6uhrmittag/todoist-progressbar/issues)

## Versioning

See [github.com/6uhrmittag/todoist-progressbar/](https://github.com/6uhrmittag/todoist-progressbar/) for source files.

## Authors

* **Marvin Heimbrodt** - *Initial work* - [slashlog.de](https://slashlog.de)
