## General

- [MD Cheatsheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)

## Todoist API

- [Todoist sync API Doc](https://developer.todoist.com/sync/v7/)
- [Todoist python sdk](https://github.com/Doist/todoist-python)


## Dropbox API
- [python sdk](https://github.com/dropbox/dropbox-sdk-python)
- [python sdk Doc](https://dropbox-sdk-python.readthedocs.io/en/latest/)
- [API Explorer](https://dropbox.github.io/dropbox-api-v2-explorer/)
- [python Example - Upload/Download](https://github.com/dropbox/dropbox-sdk-python/blob/master/example/updown.py)

## Github
- [Github API](https://developer.github.com/v3/)
- [PyGithub python sdk](https://github.com/PyGithub/PyGithub)
- [PyGihub doc](https://pygithub.readthedocs.io/en/latest/apis.html)


# install
## install from test.pypi.org
installing requirements doesn't work 100% with test.pypi.org, so they must be installed manually


python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
python3 -m pip install --user --upgrade pip
pip install Click
pip install configparser
pip install dropbox
pip install PyGithub
pip install todoist-python
pip install requests
pip install -i https://test.pypi.org/simple/ taskbutler


