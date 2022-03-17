#!/bin/sh

# Author: Soubhagya Sahoo

pip install virtualenv
virtualenv env
source env/bin/activate
pip install -r requirements.txt
flask run