BISTRO_Dashboard
====================

Visualizations of BISTRO Results

Usage
-----

To run the app, type:
::
	bokeh serve --show BISTRO_Dashboard/

Your browser will then open to: `http://localhost:5006/BISTRO_Dashboard`.

It may take a minute or so for the dashboard to load up, depending on how many submissions you are
comparing. Once it loads up, use the dropdown menus to choose the two scenario-submission pairs that 
you want to compare.

Installation
------------
To pull down the repo, type this into your terminal in the directory you want this installed:
::
	git clone https://github.com/bistro-its-berkeley/BISTRO_Dashboard.git

Create a virtual environment to install your python packages in, and install the requirements.
::
	virtualenv env
	. env/bin/activate
	pip install -r requirements.txt

Database
------------
BISTRO_Dashboard depends on MySQL database that stores BISTRO simulation data. To connect to existing database, fill in the blanks in `BISTRO_Dashboard/dashboard_profile.ini` with the credentials. If the database is not hosted on the local machine, also change **DATABASE_HOST** value to the IP address of the intended database server.

Requirements
^^^^^^^^^^^^
See requirements.txt

Compatibility
-------------

Licence
-------

Authors
-------

`BISTRO-Dashboard` was written by `Jonny Lee <jonny@uber.com>`_, `Valentine Golfier-Vetterli <vgolfi@ext.uber.com>`_, `Sidney Feygin
<sfeygi@ext.uber.com>`_, `Jessica Lazarus <jlazar2@ext.uber.com>`_, and `Robert Zangnan Yu <yuzan@berkeley.edu>`_.
