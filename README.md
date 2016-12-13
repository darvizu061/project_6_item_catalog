# Project: Item Catalog
###### Udacity Full Stack ND
#### About The Project
---
This project was created in part of Udacity's Full Stack Nanodegree curriculum. The site is title Narnes & Boble and showcases various books sorted by their genre.

This dynamic web application uses the SQLAlchemy framework to create and structure the database tables. Furthermore, it uses Flask to create the page routes and handle other server configuration tasks. With these tools, Narnes & Boble is able to perform CRUD tasks on the database from user input on the site.

In addition, Narnes & Boble uses Google's OAuth authentication and authorization services, enabling users to login to the site through their gmail account, and has RESTful API endpoints that return JSON files.
#### Getting Started
---
###### Installing dependency libraries
Install the dependency libraries (Flask, sqlalchemy, requests and oauth2client) by running `pip install -r libraries.txt`
###### Installing & Populating the Database
First, create the database by running `python database_setup.py`

Then, populate the database with the `database_seed.py` file provided by running `python database_seed.py`.
###### Running the web application
After downloading dependencies and setting up the database, run `python app.py`.
#### Google's OAuth Third-Party services
---
For the sake of providing an easy setup process, I have left my Google App credentials which can be seen in `client_secrets.json`. If you wish to implement your app's credentials, you can do so by creating and downloading them at https://console.developers.google.com. 
#### Copyright
---
This project is free of any copyrights and open to the public.
