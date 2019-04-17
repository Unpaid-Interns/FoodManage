# Developer Guide
### High Level Structure
The system is divided into 6 apps, each with a specific purpose, that integrate together into the full site, allowing for the management of Food manufacturing.
The apps are as follows:
* home: Handles the login page, the help page, role based access control, and the main menu
* importer: Handles bulk imports of information to the database
* sku_manage: Handles the storage and display of all SKU related information (SKUs, Product Lines, etc)
* manufacturing_goals: Handles the storage and displaying of manufacturing goals used for production. Also handles the manufacturing schedule storage and displays, as well as the auto-scheduler, as well as the sales projections when creating or editing a manufacturing goal.
* dep_report: Handles the displaying and exporting of the ingredient dependency report
* mfg_map: Handles the mapping of manufacturing lines to SKUs
* sales: Handles all of the sales reporting functionality, including the models used to store the data in the database and the screen-scraping functionality to access data from the company's internal sales tracking system.

Additionally, the exporter directory has the backend code for the bulk exports of items imported by the importer or created in the database.
### Technologies Used
The system was constructed using the Django framework which uses Python to drive the database interactions with a PostgreSQL database, and logic used to manipulate data for displaying and storage. Views are driven by Python and templates rendered in html files (augmented with CSS and JavaScript as needed) with template tags that can generate elements on the page based on information provided by the Python logic. The manufacturing schedule made use of vis.js as a general structure for the timeline visual interface.
### Environment Setup
The development environment was built within a Linux machine running Ubuntu 16.04 LTS. The environment requires the installation and usage of the following: 
* Python 3.5.2 (or later)
* Django 2.1.5 (with pip)
* django-tables2 (with pip)
* django-bootstrap3 (with pip)
* psycopg2-binary (with pip)
* requests (with pip)

Python 3 is usually installed with Ubuntu 16.04 and can be used to run commands in terminal by typing `python3`. Pip is installable via the command `sudo apt-get install pip3`. The remaining Python packages can be installed using `pip3 install <PACKAGE_NAME>`. The use of a virtual environment is not neccessary but is recommended.
### Development Build Deployment
To test the site for development, a few steps are needed before a test server can be deployed if any models have been edited or created.
1. run `python3 manage.py makemigrations`, or `python3 manage.py makemigrations <APP_NAME>` if the app in question does not contain a folder in its directory named migrations
2. run `python3 manage.py migrate`

If there are errors in the process, delete `db.sqlite3` and the migrations folders in each app that has them, then run `python3 manage.py makemigrations <APP_NAME>` for the apps with recently deleted migrations folders.

Otherwise, run `python3 manage.py runserver` to activate the test server, which is available to view as though it were a production site at http://127.0.0.1:8000/.
### Database and Model Layout
Our model is managed thru Django and is broken into the following data structures
* Ingredient
* ProductLine
* SKU
* Formula
* ManufacturingLine
* IngredientQty
* ManufacturingGoal
* ManufacturingQty
* ScheduleItem
* Customer
* SalesRecord
* ProductManager

Each of the first five data structures stores information related to that item.  IngredientQty is used to store the (Ingredient, Quantity) tuples related to a given SKU.  

Additionally, users' manufacturing goals are stored in the database in two tables.  ManufacturingGoal links manufacturing goals to specific users, and ManufacturingQty stores the contents of manufacturing goals in (SKU, Qty) tuples specific to each manufacturing goal.

Timeline information is stored by ScheduleItem, which effectively stores a tuple of (ManufacturingQty, ManufacturingLine) associated with a manufacturing activity to be shown on the timeline. It also stores the start time and end time of the activity as optional fields depending on the placement of activities by the administrator, and contains logic to calculate the item's expected duration.

Sales reporting includes two models: Customer, which stores a name and unique identifying number for each customer, and SalesRecord, which, for each item in the report, keeps track of the SKU, the date of sale, the customer (as a foreign key),  the number of cases sold, and the price per case.

For role based access control, Django was able to natively handle the vast majority of determining what each role was allowed to handle, and most roles were created through both Django's native RBAC and internal logic to connect specific permissions to specific roles. For Product Managers, however, a new model called ProductManager had to be created to link an appropriate user with specific Manufacturing Lines using foreign keys.

#### Database Schema
![alt text](https://i.imgur.com/8OFwpQC.png "Database Schema")
