# app/lib/decorators.py

from flask import flash, redirect, url_for
from flask_login import current_user
from markupsafe import Markup
from functools import wraps
from ..config.settings import accountlist_title, domainlist_title
from ..models.models import Domain, User


def siteadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'domainid' in kwargs:
            domainid = kwargs['domainid']
        else:
            domainid = 0

        if not current_user.is_siteadmin:
            flash(Markup('The requested functionality is reserved for siteadmins.'), 'error')
            print(str(current_user.is_postmaster) + '    ' + str(domainid))
            if current_user.is_postmaster > 0:
                return redirect(url_for('home.postmaster'))
            return redirect(url_for('home.user'))

        return f(*args, **kwargs)

    return decorated_function


def postmaster_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'domainid' in kwargs:
            domainid = kwargs['domainid']
        else:
            domainid = User.query.one(kwargs['accountid']).domain_id

        if not (current_user.is_postmaster == domainid
            or current_user.is_siteadmin):
            flash(Markup('The requested functionality is reserved for postmasters.'), 'error')
            return redirect(url_for('home.user'))

        return f(*args, **kwargs)

    return decorated_function


def accounttyp_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if kwargs['accounttype'] not in accountlist_title:
            flash(Markup('We don\'t know the accounttype <b>' + kwargs['accounttype'] + '</b>.'), 'error')
            # redirect to domainlist page
            return redirect(url_for('accounts.accountlist', domainid=kwargs['domainid'], accounttype='local'))

        return f(*args, **kwargs)

    return decorated_function


def domaintyp_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if kwargs['domaintype'] not in domainlist_title:
            flash(Markup('We don\'t know the domaintype <b>' + kwargs['domaintype'] + '</b>.'), 'error')
            return redirect(url_for('domains.domainlist', _anchor=kwargs['domainid'], domaintype='local'))

        return f(*args, **kwargs)

    return decorated_function
