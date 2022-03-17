# picsearch-Flask
This is a back-end application made with FLask which has a collection of the API endpoints which are used by the fornt-end made with Angular.
Basic functionalitie like user login/ logout, registration, searching for pictures based on location details, adding and removing
pictures from favorites, saving location details to database have been made. Make sure to check for the basic requirements before running the application.

**Prerequisites**
Python 3.7.x or above.
If you do not have python3 you can install it from here:
https://www.python.org/downloads/

For geting hands on ORM techniques(sqlalchemy), you can check this link:
https://www.tutorialspoint.com/sqlalchemy/index.htm

Follow this link for PEP8 guidelines:
https://peps.python.org/pep-0008/

**Steps for setting up the project:**

_Install virtualenvironment_
> pip install virtualenv

_Create a virtual environment for the project for installong required libraries and then activate it_
> virtualenv env_name or venv env_name  
> source env_name/bin/activate (for activating in linux)  
> env_name\Scripts\activate (for activating in windows)  

_Install the required libraries_
> pip install -r requirements.txt

** Make sure the database server is running locally or remotely as per the connections made.

_Run the application_
> flask run

Use postman for working with the routes present in the application.

**To automate the setup**

Make sure the database server is running.
Check for the connection in the _app.py_ file. The _conf_ variable stores the database configuration. Choose accordingly for mysql or postgresql.

Run the _run.sh_ file 
> source run.sh
* Source is required to run the script as for activating the virtual environmwnt from the script, we will be needing source.

The script will automatically install all required libraries to the virtual environment and run the application.