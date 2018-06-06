# app/home/__init__.py
# This file is part of veximpy

from flask import Blueprint

home = Blueprint('home', __name__)

from . import views
