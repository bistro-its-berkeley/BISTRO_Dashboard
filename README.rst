Dashboard_Uber_Prize
====================

.. image:: https://img.shields.io/pypi/v/Dashboard_Uber_Prize.svg
    :target: https://pypi.python.org/pypi/Dashboard_Uber_Prize
    :alt: Latest PyPI version

Visualizations of Uber Prize Results

Usage
-----
Unless you provide a custom `submission_files_override.csv` file, the dashboard app will search your 
data directory for scenario-submission pairs to show. It will automatically hide any pairs that it 
knows about but can not find. It will automatically add and show any pairs that it did not
previously know about. To manually override the show/hide settings, you may edit the second 
column in `submission_files.csv` or provide your custom `submission_files_override.csv` file.

To run the app, type:
::
	bokeh serve --show Dashboard_Uber_Prize/

Your browser will then open to: `http://localhost:5006/Dashboard_Uber_Prize`.

It may take a minute or so for the dashboard to load up, depending on how many submissions you are
comparing. Once it loads up, use the dropdown menus to choose the two scenario-submission pairs that 
you want to compare.

Installation
------------
To pull down the repo, type this into your terminal in the directory you want this installed:
::
	git clone https://github.com/vgolfier/Dashboard_Uber_Prize.git

Create a virtual environment to install your python packages in, and install the requirements.
::
	virtualenv env
	. env/bin/activate
	pip install -r requirements.txt

Requirements
^^^^^^^^^^^^
See requirements.txt

Compatibility
-------------

Licence
-------

Authors
-------

`Dashboard_Uber_Prize` was written by `Jonny Lee <jonny@uber.com>`_, `Valentine Golfier-Vetterli <vgolfi@ext.uber.com>`_, `Sidney Feygin
<sfeygi@ext.uber.com>`_, and `Jessica Lazarus <jlazar2@ext.uber.com>`_.