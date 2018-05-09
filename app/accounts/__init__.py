# app/accounts/__init__.py

from flask import Blueprint

accounts = Blueprint('accounts', __name__, template_folder='templates/accounts')

from . import views_accounts

