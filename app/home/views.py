# app/home/views.py

from flask import redirect, render_template, url_for
from flask_login import current_user, login_required

from . import home

global projectname
projectname = 'vexim - Virtual Exim'

@home.route('/')
def homepage():
    """
    Redirect to login page
    """

    if current_user.is_active:
        if current_user.is_siteadmin:
            return redirect(url_for('domains.domainlist', domaintype='local'))
        elif current_user.is_postmaster:
            return redirect(url_for('accounts.accountlist', domaintype='local'))
        else:
            return redirect(url_for('home.index.html'))
    return redirect(url_for('auth.login'))

@home.route('/user')
def user():
    """
    Render the homepage template on the /user route
    """
    return render_template('home/index.html', title="Welcome")

@home.route('/siteadmin')
@login_required
def siteadmin():
    """
    Render the dashboard siteadmin on the /siteadmin route
    """
    #return render_template('home/siteadmin.html', title="Siteadmin")
    return redirect(url_for('domains.domainlist', domaintype='local'))

@home.route('/postmaster')
@login_required
def postmaster():
    """
    Render the postmaster template on the /postmaster route
    """

    #return render_template('home/postmaster.html', title="Postmaster")
    return redirect(url_for('accounts.accountlist', domainid=current_user.is_postmaster, domaintype='local'))
