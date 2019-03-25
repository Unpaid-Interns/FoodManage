#!/bin/bash

# Check directory
if pwd | grep -q "FoodManage/scripts"; then
	cd ..
fi
if ! [ -d food_site ]; then
	echo "Run script from inside project"
	exit
fi

# Warn user
echo "Warning: This performs a hard reset on the database"
echo "DO NOT USE THIS SCRIPT - Nathaniel"
echo "Are you sure you want to continue (y/N)"
read resp
if ! echo "$resp" | grep -q "y"; then
	echo "Exiting"
	exit
fi
echo "Resetting database"

# Clear database
rm food_site/db.sqlite3
dropdb food_db
createdb food_db

# Clear migrations
rm food_site/*/migrations/*auto*.py
rm food_site/*/migrations/*initial.py
rm  -r food_site/*/migrations/__pycache__

# Re-initialize database
if [ -d site_env ]; then
	source site_env/bin/activate
	./food_site/manage.py makemigrations
	./food_site/manage.py migrate
	echo "Set admin password"
	./food_site/manage.py createsuperuser --username admin --email admin@hypomeals.com
	deactivate
else
	python3 food_site/manage.py makemigrations
	python3 food_site/manage.py migrate
	echo "set admin password"
	python3 food_site/manage.py createsuperuser --username admin --email admin@hypomeals.com
fi

# Restart server
sudo service apache2 restart