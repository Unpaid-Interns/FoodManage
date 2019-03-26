# Deployment Guide
### Installation and Deployment
1. Acquire a linux server.
  * Current software was designed for a server running Ubuntu 16.04
2. Run scripts/install.sh
  * Installs all software dependencies
 
### Deploy and Restore from Backup
1. Install as above
2. Make sure the database is empty
3. Get the backup file from the backup server
4. Rename the file to have a .json extension
5. run `python manage.py loaddata <FILE_NAME>`
