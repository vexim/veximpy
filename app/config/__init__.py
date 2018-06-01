# app/config/__init__.py

from flask import Blueprint

config = Blueprint('config', __name__)

from . import views
from . import config
