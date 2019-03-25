# Backup Guide for Administrators

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
