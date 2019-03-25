#!/bin/bash

# Go to correct directory
if ! pwd | grep -q "FoodManage/scripts"; then
	cd ~/FoodManage/scripts
fi
if ! pwd | grep -q "FoodManage/scripts"; then
	echo "Run from scripts folder"
	exit
fi

# Run Background Scheduler
source ../site_env/bin/activate
python ../food_site/manage.py process_tasks --duration 3600 --sleep 1 --log-std
deactivate

