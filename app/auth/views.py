# app/auth/views.py

import validators
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from markupsafe import Markup
from . import auth
from .forms import LoginForm
#from app.app import db, session_domain_id
from ..models.models import User
from ..home.views import redirect_home

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle requests to the /login route
    Log an user in through the login form
    Try some magic if the given username is not found in the DB by guessing and adding a domainname 
    """
    global session_domain_id
    session_domain_id = None

    def try_login(user):
        global session_domain_id
        # check whether user exists in the database and whether
        # the password entered matches the password in the database
        if user is not None and user.verify_password(form.password.data):
            # log user in
            login_user(user)
            session_domain_id = user.domain_id
            return True
        return False

    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter(User.username==form.username.data).one_or_none()
        # if username did not match any user in the database
        # try to construct an user by adding a domainname guessed from the request.host and try login
        if not try_login(user=user) and validators.domain(request.host.partition(':')[0]):
            # iterate through subdomains of request.host
            # strip one subdomain from left on each iteration
            domainname = request.host
            for dn in domainname:
                un = form.username.data + '@' + domainname
                # compare with username field and try login
                user = User.query.filter(User.username==un).one_or_none()
                # break if we have found the user
                if try_login(user=user):
                    break
                # compare with localpart and domain fields and try login
                user = User.query.filter(User.localpart==form.username.data, User.domainname==domainname).one_or_none()
                # break if we have found the user or if we reached the main domain
                if try_login(user=user) or domainname.count('.') == 1:
                    break
                domainname = domainname.partition('.')[2]

        # if a session_domain_id was assigned, we got a valid login
        if session_domain_id == None:
            flash('Invalid user or password.', 'error')
        elif user.is_active:
            flash(Markup('Login succeded for user <b>' + user.username + '</b>'),  'success')
        else: # if not user.is_active
            flash(Markup('User <i>' + str(user.username) + '</i> is disabled.'), 'warning')
        return redirect_home()

    # load login template
    return render_template('auth/login.html', domainname = request.host, form=form, title='Login')


@auth.route('/logout')
@login_required
def logout():
    """
    Handle requests to the /logout route
    Log an user out through the logout link
    """

    global session_domain_id

    logout_user()

    session_domain_id = 0

    flash('You have successfully been logged out.',  'success')

    # redirect to the login page
    return redirect(url_for('auth.login'))
