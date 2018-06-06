# app/auth/__init__.py
# This file is part of veximpy

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
