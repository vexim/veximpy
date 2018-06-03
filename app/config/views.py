# app/config/views.py

from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from markupsafe import Markup
#from .forms import LoginForm, RegistrationForm
from app.app import db
#from ..models.models import User
from ..lib.decorators import siteadmin_required

from . import config

@config.route('/siteconfig', methods=['GET', 'POST'])
@siteadmin_required
@login_required
def siteconfig():
    """
    Handle requests to the /siteconfig route
    Add an user to the database through the registration form
    """

    # load configuration template
    return render_template('/config/siteconfig.html', form=form, title='Site Configuration')
