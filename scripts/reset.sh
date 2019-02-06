#!/bin/bash

# Clear database
rm food_site/db.sqlite3
dropdb food_db
createdb food_db

# Clear migrations
rm food_site/*/migrations/*auto*.py
rm food_site/*/migrations/*initial.py
rm  -r food_site/*/migrations/__pycache__

# Re-initialize database
source site_env/bin/activate
./food_site/manage.py makemigrations
./food_site/manage.py migrate
./food_site/manage.py createsuperuser --username admin --email admin@hypomeals.com
deactivate

# Restart server
sudo service apache2 restart