#!bin/bash

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
./food_site/manage.py collectstatic
deactivate