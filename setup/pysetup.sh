#!/bin/bash
# This file is part of veximpy

# Install Python packages in the system
sudo apt install mariadb-server python3 python3-venv python3-pip python3-pytest python3-flask python3-flask-login python3-flask-migrate python3-dotenv python3-passlib python3-flaskext.wtf python3-validators python3-wtforms python3-pymysql python3-sqlalchemy
sudo apt install nginx-full uwsgi uwsgi-plugin-python3
sudo pip3 install flask_bootstrap flask_debugtoolbar wtforms

# Create Virtual Environment
python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt
ln -s venv/bin/activate


echo "export FLASK_CONFIG=development; export FLASK_APP=run.py; export PYTHONPATH=${PYTHONPATH}:$(pwd)" >> activate

# Prepare the config files for uwsgi and nginx
sed "s/###dir###/$(pwd)/" doc/nginx/veximpy.template > doc/nginx/veximpy
sed "s/###dir###/$(pwd)/" doc/uwsgi/veximpy.ini.template > doc/uwsgi/veximpy.ini

if [[ ! -z ${1} ]]; then
    sed "s/###servername###/${1}/" doc/nginx/veximpy.template > doc/nginx/veximpy
fi

echo "you will find sample config files for nginx and uwsgi in doc/{nginx|uwsgi} directories"
echo "make sure to use the correct path for certificates and the correct servername"
echo "you should be able to activate the python environment with \`. activate\`"
