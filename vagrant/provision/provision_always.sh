#!/usr/bin/env bash

echo "Provision always:"
sudo apt-get -y install xvfb libfontconfig wkhtmltopdf
su - vagrant -c "
cd /vagrant
workon vagrant && \
pip3 install -r /vagrant/requirements/local.txt && \
python manage.py migrate --noinput --settings=config.settings.local && \
python manage.py collectstatic --noinput --settings=config.settings.local"

if ! [ $(find /vagrant -maxdepth 1 -name '.env' | wc -l) -gt 0 ]; then
    cp -p /vagrant/vagrant/templates/env.vagrant /vagrant/.env
fi

