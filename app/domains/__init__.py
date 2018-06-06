# app/domains/__init__.py
# This file is part of veximpy

from flask import Blueprint

domains = Blueprint('domains', __name__, template_folder='templates/domains')

from . import views
