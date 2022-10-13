#!/bin/bash
export WORKON_HOME=~/envs
source /usr/local/bin/virtualenvwrapper.sh
alias rs="python manage.py runserver 0.0.0.0:8000"
workon vagrant
cd /vagrant/
