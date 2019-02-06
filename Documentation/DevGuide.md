# Developer Guide
### High Level Structure
The system is divided into 6 apps, each with a specific purpose, that integrate together into the full site, allowing for the management of Food manufacturing.
The apps are as follows:
* home: Handles the login page, the help page, and the main menu
* importer: Handles bulk imports of information to the database
* exporter: Handles bulk exports of information from the database
* sku_manage: Handles the storage of all information (SKUs, Product Lines, etc)
* manufacturing_goals: Handles the storage and displaying of manufacturing goals used for production
* dep_report: Handles the displaying and exporting of the ingredient dependency report
### Technologies Used
The system was constructed using the Django framework which uses Python to drive the database interactions and logic used to manipulate data for displaying and storage. Views are driven by Python and templates rendered in html files (augmented with CSS and JavaScript as needed) with template tags that can generate elements on the page based on information provided by the Python logic.
### Environment Setup
The development environment was built within a Linux machine running Ubuntu 16.04 LTS. The environment requires the installation and usage of the following: 
* Python 3.5.2 (or later)
* Django 2.1.5 (with pip)
* django-tables2 (with pip)
* django-filter (with pip)
* django-bootstrap3 (with pip)
* psycopg2-binary (with pip)

Python 3 is usually installed with Ubuntu 16.04 and can be used to run commands in terminal by typing `python3`. Pip is installable via the command `sudo apt-get install pip3`. The remaining Python packages can be installed using `pip3 install <PACKAGE_NAME>`. The use of a virtual environment is not neccessary but is recommended.
### Database and Model Layout
