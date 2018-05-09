# app/config/__init__.py

from flask import Blueprint

config = Blueprint('config', __name__)

from . import views_siteconfig
from . import config
