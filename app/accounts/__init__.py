# app/accounts/__init__.py
# This file is part of veximpy

from flask import Blueprint

accounts = Blueprint('accounts', __name__, template_folder='templates/accounts')

from . import views

