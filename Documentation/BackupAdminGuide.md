# Backup Guide for Administrators

## Backup environment
The backup environment needs to be a server running a Linux system that runs continuously and is accessible via SSH. The backup server at least needs the contents of the `backup` folder in the directory.

To configure the production server to backup once daily, the neccessary scripts are located within the `backup` directory of the project. Create a cron job on the production server that runs at the desired time and time interval, and have the cron job run the `backup.sh` shell script to carry out the process of backing up the server's database and sending it to the backup server. Within `backup.sh`, the line beginning with `scp` should have the listed address replaced with the domain or IP associated with the desired backup server.

A separate cron job on the backup server needs to be configured to run at a desired time and interval after the time period of the other cron job. This job should execute the `backup_script.sh` shell script, which runs the associated python script that handles the appropriate sorting of the backup files and notification of system administrators upon successful or failed backups.

## Daily backups
At 1 AM EST daily a new backup file is sent to the backup server from the production server via SSH, with a date stamp in the file name. 

At 2 AM EST daily the backup server's system checks for a new backup file. If one is found, it moves the file into the daily backup directory. It then checks to see if there are more than 7 files in the daily backup directory. If that is the case, the system moves the earliest file chronologically from the daily backup directory into the weekly backup directory.

The following example demonstrates the backup system and the movement of files from the daily backup directory and into the weekly directory:
- March 1, 2, 3, 4, 5, 6, and 7th are all sent to the daily backup directory.
- March 8th is sent to the daily backup directory. The directory is now over capacity.
  - March 1st backup is moved to the weekly backup directory.
- March 9th is sent to daily backup directory. The directory is now over capacity.
  - March 2nd is removed from the daily directory.
- A week after March 8th, March 15th is sent to daily backup directory. The directory is now over capacity.
  - March 8th is moved to the weekly backup directory.

## Recovering a file
To recover the production database, first either make sure the production database is empty either by running `python manage.py flush` or by deleting the database manually as well as the migrations files in each folder of the project (in which case, run `python manage.py makemigrations <FOLDER_NAME>` for each and run `python manage.py migrate` to reform the database). To retrieve a file from the backup server, connect to the server via SSH in terminal and transfer the file to the desired location. Rename the file to have a .json extension, then run `python manage.py loaddata <FILE_NAME>` to recover the production database to the desired recovery point.
