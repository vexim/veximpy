#!/bin/bash

sudo apt install python3 python3-venv python3-pip
python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt
ln -s venv/bin/activate
echo "export FLASK_CONFIG=development; export FLASK_APP=run.py; export PYTHONPATH=${PYTHONPATH}:$(dirname ${0})" >> activate

sed "s/###dir###/$(dirname ${0})/" doc/nginx/veximpy.template > doc/nginx/veximpy
sed "s/###dir###/$(dirname ${0})/" doc/uwsgi/veximpy.ini.template > doc/uwsgi/veximpy.ini

if [[ ! -z ${1} ]]; then
    sed "s/###servername###/${1}/" doc/nginx/veximpy.template > doc/nginx/veximpy
fi

echo "you will find sample config files for nginx and uwsgi in doc/{nginx|uwsgi} directories"
echo "make sure to use the correct path for certificates and the correct servername"
echo "you should be able to activate the python environment with \`. activate\`"
