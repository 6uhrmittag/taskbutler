#!/usr/bin/env bash

# install requirements
apt-get update
sudo apt-get install -y python3-setuptools python3-pip python3-venv libffi-dev python3-dev
# requirements by dh-virtualenv
sudo apt-get install -y build-essential debhelper devscripts equivs
sudo apt-get install -y devscripts python-virtualenv python-sphinx python-sphinx-rtd-theme git equivs

# fix possible issues automatically
sudo apt-get -y -f install

python3 -m pip install --user --upgrade setuptools wheel


# install dh -virtualenv
git clone https://github.com/spotify/dh-virtualenv.git
cd dh-virtualenv
dpkg-buildpackage -us -uc -b
sudo find ../ -name dh-virtualenv*.deb -exec dpkg -i {} \;
cd

ls# build package
git clone https://github.com/6uhrmittag/taskbutler.git
cd taskbutler
git fetch origin
git branch -v -a
git checkout -b debian remotes/origin/feature-githubsync

# install initial debian files
#pip install make-deb
#make-deb

dpkg-buildpackage -us -ucvi