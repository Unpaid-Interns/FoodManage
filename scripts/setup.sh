#!bin/bash

# Update from repository
git pull

# Setup Python Virtal Environment
if [ -d /site_env ]; then
	python3 -m virtualenv site_env
fi

# Install and update python packages
source site_env/bin/activate
pip install --upgrade django
pip install --upgrade django-tables2
pip install --upgrade django-filter
pip install --upgrade django-bootstrap3
pip install --upgrade psycopg2-binary

# Setup Django
./food_site/manage.py migrate
./food_site/manage.py collectstatic
./food_site/manage.py createsuperuser --username admin --email admin@hypomeals.com
deactivate