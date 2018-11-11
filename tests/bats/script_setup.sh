#!/usr/bin/env bash
sudo apt-get -y install python3
python3 -m pip install --user --upgrade pip
python3 -m virtualenv venv
source venv/bin/activate
pip install taskbutler