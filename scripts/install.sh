#!/bin/bash

# Check directory
if [ pwd | grep -q "FoodManage/scripts" ]; then
	cd ..
fi
if ! [ -d food_site ]; then
	echo "Run script from inside project"
	exit
fi

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

# Install and configure postgres
echo "Enter a password to use with your database"
read DB_PASS
sudo apt-get -qq -y install postgresql postgresql-contrib
if ! sudo -s sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$user'" | grep -q 1; then
    sudo -s sudo -u postgres createuser -s $user
    sudo -s sudo -u postgres psql -c "ALTER USER $user WITH PASSWORD '$DB_PASS'"
fi

# Install python and virtualenv
sudo apt-get -qq -y install python3
sudo apt-get -qq -y install python3-pip
pip3 install --upgrade pip3
pip3 install --upgrade virtualenv

# Configure apache allowed-hosts
FILEPATH=$(pwd)
OLD_CONFIG="</VirtualHost>"
NEW_CONFIG="    Alias /static $FILEPATH/food_site/static\n    <Directory $FILEPATH/food_site/static>\n        Require all granted\n    </Directory>\n\n    <Directory $FILEPATH/food_site/food_site>\n        <Files wsgi.py>\n            Require all granted\n        </Files>\n    </Directory>\n\n    WSGIDaemonProcess food_site_daemon python-path=$FILEPATH/food_site python-home=$FILEPATH/site_env\n    WSGIProcessGroup food_site_daemon\n    WSGIScriptAlias / $FILEPATH/food_site/food_site/wsgi.py\n\n</VirtualHost>"
sudo sed -i "s*$OLD_CONFIG*$NEW_CONFIG*g" /etc/apache2/sites-available/000-default-le-ssl.conf
if ! cat /etc/apache2/sites-available/000-default-le-ssl.conf | grep -q "food_site"; then
	echo "Failed to configure apache server. exiting"
	exit
fi
# Note: may need to also configure non-ssl allowed hosts file

# Set apache permissions for upload
sudo chmod a+w /var/www

# Copy jank-ass help pdf to correct place
mkdir /var/www/importer
cp -i food_site/importer/import_instructions.pdf /var/www/importer/import_instructions.pdf

# Configure postgres to allow apache access
OLD_PCONF="# TYPE  DATABASE        USER            ADDRESS                 METHOD\n\n# "local" is for Unix domain socket connections only\nlocal   all             all                                     peer"
NEW_PCONF="# TYPE  DATABASE        USER            ADDRESS                 METHOD\n\n# "local" is for Unix domain socket connections only\nlocal   all             all                                     md5"
sudo -s -u postgres sed -i "s/$OLD_PCONF/$NEW_PCONF/g" /etc/postgresql/**/main/pg_hba.conf
if ! cat /etc/postgresql/**/main/pg_hba.conf | grep -q "local   all             all                                     md5"; then
	echo "Failed to configure PostgreSQL. exiting"
	exit
fi

# Restart postgres to reflect changes
sudo service postgresql restart

# Create database
createdb food_db

# Setup python virtal environment
if ! [ -d site_env ]; then
	python3 -m virtualenv site_env
fi

# Install and update python packages in virtual environment
source site_env/bin/activate
pip install --upgrade django
pip install --upgrade django-tables2
pip install --upgrade django-filter
pip install --upgrade django-bootstrap3
pip install --upgrade psycopg2-binary

# Configure django settings
python -c 'import random; import os; result = "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)]); os.environ["SECRET_KEY"] = result'
deactivate
OLD_SETTINGS="    'default': {\n        'ENGINE': 'django.db.backends.sqlite3',\n        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),\n    }"
NEW_SETTINGS="    'default': {\n        'ENGINE': 'django.db.backends.postgresql_psycopg2',\n        'NAME': 'food_db',\n        'USER': '$user',\n        'PASSWORD': '$DB_PASS',\n        'HOST': '',\n        'PORT': '',\n    }"
sed -i "s/$OLD_SETTINGS/$NEW_SETTINGS/g" food_site/food_site/settings.py
OLD_DEBUG="DEBUG = True"
NEW_DEBUG="DEBUG = False"
sed -i "s/$OLD_DEBUG/$NEW_DEBUG/g" food_site/food_site/settings.py

# Setup django
source site_env/bin/activate
./food_site/manage.py makemigrations -v 0
./food_site/manage.py migrate -v 0
./food_site/manage.py collectstatic --noinput -v 0
./food_site/manage.py createsuperuser --username admin --email admin@hypomeals.com
deactivate

# Restart apache to reflect changes
sudo service apache2 restart
