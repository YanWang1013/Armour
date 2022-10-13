echo "Installing system packages"
apt-get update -y
apt-get install -y build-essential python-pip python-dev mc git libffi-dev dos2unix python3-dev python3-pip

# Dependencies for virtualenv
apt-get install -y libjpeg8 libjpeg8-dev libtiff-dev zlib1g-dev libfreetype6-dev liblcms2-dev libxml2-dev libxslt1-dev libffi-dev libssl-dev swig libyaml-dev libpython2.7-dev

# graphics support for Pillow (jpg, png etc)
apt-get -y build-dep python-imaging sudo
apt-get install -y libjpeg8 libjpeg62-dev libfreetype6 libfreetype6-dev
apt-get install -y memcached redis-server postgresql postgresql-contrib postgresql-server-dev-all postgresql-client-common

#Python3
apt-get -y install python3-dev

#postgesql
sudo -u postgres createuser -d -s vagrant
sudo -u postgres createdb -O vagrant vagrant
sudo -u postgres psql -U postgres -d postgres -c "ALTER USER vagrant WITH PASSWORD 'vagrant';"

echo "Setting up pip and virtualenv"
pip install virtualenv
pip install virtualenvwrapper

cp -p /vagrant/templates/.env.vagrant /vagrant/.env

echo "Creating virtualenv and configuring app"
su - vagrant -c "mkdir -p /home/vagrant/envs"
su - vagrant -c "export WORKON_HOME=~/envs && \
source /usr/local/bin/virtualenvwrapper.sh && \
mkvirtualenv -p python3 vagrant"

cp -p /vagrant/templates/.bashrc /home/vagrant/.bashrc
