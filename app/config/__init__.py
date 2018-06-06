# app/config/__init__.py
# This file is part of veximpy

from flask import Blueprint

config = Blueprint('config', __name__)

from . import views
from . import config
