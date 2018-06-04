# app/home/views.py

from flask import redirect, url_for
from flask_login import current_user, login_required

from . import home

global projectname
projectname = 'vexim - Virtual Exim'

def redirect_home():
    if current_user.is_active:
        if current_user.is_siteadmin:
            return redirect(url_for('home.siteadmin'))
        elif current_user.is_postmaster > 0:
            return redirect(url_for('home.postmaster'))
        return redirect(url_for('home.user'))
    else:
        return redirect(url_for('auth.login'))

@home.route('/')
def homepage():
    """
    Redirect to login page
    """
    return redirect_home()

@home.route('/user')
def user():
    """
    Render the homepage template on the /user route
    """
    return redirect(url_for('accounts.account_edit', accountid=current_user.id, accounttype=current_user.type))

@home.route('/siteadmin')
@login_required
def siteadmin():
    """
    Render the dashboard siteadmin on the /siteadmin route
    """
    return redirect(url_for('domains.domainlist', domaintype='local'))

@home.route('/postmaster')
@login_required
def postmaster():
    """
    Render the postmaster template on the /postmaster route
    """
    return redirect(url_for('accounts.accountlist', domainid=current_user.is_postmaster, accounttype='local'))
