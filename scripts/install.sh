#!bin/bash

# Update apt
sudo apt-get -qq update

# Install apache
sudo apt-get -qq -y install apache2

# Install certbot
sudo apt-get -qq -y install software-properties-common
sudo add-apt-repository -y universe
sudo add-apt-repository -y ppa:certbot/certbot
sudo apt-get -qq update
sudo apt-get -qq -y install certbot python-certbot-apache 
sudo certbot --apache

# Install postgres
sudo apt-get -qq -y install postgresql postgresql-contrib
if ! sudo -s sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$user'" | grep -q 1; then
    sudo -s sudo -u postgres createuser -s $user
    sudo -s sudo -u postgres psql -c "ALTER USER $user WITH PASSWORD '$kr|k-*@WPbm5vau'"
fi

# Install python and virtualenv
sudo apt-get -qq -y install python3
sudo apt-get -qq -y install python3-pip
pip3 install --upgrade pip3
pip3 install --upgrade virtualenv

# Restart services
sudo service postgresql restart
sudo service apache2 restart