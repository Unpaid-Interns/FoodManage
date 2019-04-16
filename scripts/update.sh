#!/bin/bash

# Check directory
if pwd | grep -q "FoodManage/scripts"; then
	cd ..
fi
if ! [ -d food_site ]; then
	echo "Run script from inside project"
	exit
fi

# Update from repository
git pull

# Setup Django
source site_env/bin/activate
./food_site/manage.py makemigrations
./food_site/manage.py migrate
./food_site/manage.py collectstatic --noinput
deactivate

# Restart server
sudo service apache2 restart