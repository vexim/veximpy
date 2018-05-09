# app/domains/__init__.py

from flask import Blueprint

domains = Blueprint('domains', __name__, template_folder='templates/domains')

from . import views_domains
