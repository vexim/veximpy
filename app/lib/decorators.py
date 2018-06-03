# app/lib/decorators.py
# decorators
# helper functions for decorators

from flask import flash, redirect, url_for
from flask_login import current_user
from markupsafe import Markup
from functools import wraps
from ..config.settings import settings, accountlist_title, domainlist_title
#from ..models.models import Domain, User


def siteadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_siteadmin:
            flash(Markup('The requested functionality is reserved for siteadmins.'), 'error')
            if current_user.is_postmaster > 0:
                return redirect(url_for('home.postmaster'))
            return redirect(url_for('home.user'))

        return f(*args, **kwargs)

    return decorated_function


def postmaster_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not (current_user.is_postmaster == _get_domainid(kwargs)
            or (current_user.is_siteadmin) and settings['SITEADMIN_ALLOWMANAGEACCOUNTS'] == 1):
            flash(Markup('The requested functionality is reserved for postmasters.'), 'error')
            if current_user.is_siteadmin:
                return redirect(url_for('home.siteadmin'))
            elif current_user.is_postmaster > 0:
                return redirect(url_for('home.postmaster'))
            return redirect(url_for('home.user'))

        return f(*args, **kwargs)

    return decorated_function


def accounttyp_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if kwargs['accounttype'] not in accountlist_title:
            flash(Markup('We don\'t know the accounttype <b>' + kwargs['accounttype'] + '</b>.'), 'error')
            return redirect(url_for('accounts.accountlist', domainid=_get_domainid(kwargs), accounttype='local'))

        return f(*args, **kwargs)

    return decorated_function


def domaintyp_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if kwargs['domaintype'] not in domainlist_title:
            flash(Markup('We don\'t know the domaintype <b>' + kwargs['domaintype'] + '</b>.'), 'error')
            return redirect(url_for('domains.domainlist', _anchor=_get_domainid(kwargs), domaintype='local'))

        return f(*args, **kwargs)

    return decorated_function


# helper functions for decorators

def _get_domainid(kwargs_dict):
    if 'domainid' in kwargs_dict:
        return kwargs_dict['domainid']
    elif 'accountid' in kwargs_dict:
        return User.query.one(kwargs_dict['accountid']).domain_id
    else:
        return 0
