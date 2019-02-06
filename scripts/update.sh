#!/bin/bash

# Check directory
if [ pwd | grep -q "FoodManage/scripts" ]; then
	cd ..
fi
if ! [ -d food_site ]; then
	echo "Run script from inside project"
	exit
fi

# Update from repository
git pull

# Update python packages
source site_env/bin/activate
pip install --upgrade django
pip install --upgrade django-tables2
pip install --upgrade django-filter
pip install --upgrade django-bootstrap3
pip install --upgrade psycopg2-binary

# Setup Django
./food_site/manage.py migrate
./food_site/manage.py collectstatic --noinput
deactivate

# Restart server
sudo service apache2 restart