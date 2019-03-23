#!/bin/bash

# Run Backup
source ~/FoodManage/site_env/bin/activate
cd ~/FoodManage/backup
python backup.py
deactivate