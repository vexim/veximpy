#!/bin/bash

python3 -m venv venv
pip3 install -r requirements.txt
ln -s venv/bin/activate
echo "export FLASK_CONFIG=development; export FLASK_APP=run.py; export PYTHONPATH=${PYTHONPATH}:$(dirname ${0})" >> activate

