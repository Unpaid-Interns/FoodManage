#!/bin/bash

# Go to correct directory
if ! pwd | grep -q "FoodManage/backup"; then
	cd ~/FoodManage/backup
fi
if ! pwd | grep -q "FoodManage/backup"; then
	echo "Run script from backup folder"
	exit
fi

# Run Backup
source ../site_env/bin/activate
python ../food_site/manage.py dumpdata > backup
DATE=$(python -c 'from datetime import date; print(date.today())')
deactivate
scp backup vcm@vcm-8261.vm.duke.edu:backup-$DATE
rm backup
