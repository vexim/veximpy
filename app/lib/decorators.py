# app/lib/decorators.py
# decorators
# helper functions for decorators

from flask import flash
from flask_login import current_user
from sqlalchemy.orm.exc import NoResultFound
from markupsafe import Markup
from functools import wraps
from ..config.settings import settings, accountlist_title, domainlist_title
from ..home.views import redirect_home

def siteadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_siteadmin:
            flash(Markup('The requested functionality is reserved for siteadmins.'), 'error')
            return redirect_home()

        return f(*args, **kwargs)

    return decorated_function


def postmaster_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        domainid = _get_domainid(kwargs)
        if not (current_user.is_postmaster == domainid
                or (current_user.is_siteadmin)
                    and settings['SITEADMIN_ALLOWMANAGEACCOUNTS'] == 1):
            flash(Markup('You have no permission for domain id <b>' + str(domainid) + '</b>.'), 'error')
            return redirect_home()

        return f(*args, **kwargs)

    return decorated_function


def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        accountid = _get_accountid(kwargs)

        if not current_user.is_authenticated:
            flash(Markup('You are not logged in.'), 'error')
            return redirect_home()

        if not (current_user.id == accountid
                or current_user.is_postmaster == _get_domainid(kwargs)
                or (current_user.is_siteadmin)
                    and settings['SITEADMIN_ALLOWMANAGEACCOUNTS'] == 1):
            flash(Markup('You have no permission for account id <b>' + str(accountid) + '</b>.'), 'error')
            return redirect_home()

        return f(*args, **kwargs)

    return decorated_function


def accountid_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'accountid' not in  kwargs:
            flash(Markup('No accountid given.'), 'error')
            return redirect_home()
        elif _get_accountid(kwargs) == 0:
            flash(Markup('Invalid accountid <b>' + str(kwargs['accountid']) + '</b>.'), 'error')
            return redirect_home()

        return f(*args, **kwargs)

    return decorated_function

def domainid_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'domainid' not in  kwargs:
            flash(Markup('No domainid given.'), 'error')
            return redirect_home()
        elif _get_domainid(kwargs) == 0:
            flash(Markup('Invalid domain id <b>' + str(kwargs['domainid']) + '</b>.'), 'error')
            return redirect_home()

        return f(*args, **kwargs)

    return decorated_function

def accounttyp_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if kwargs['accounttype'] not in accountlist_title:
            flash(Markup('We don\'t know the account type <b>' + kwargs['accounttype'] + '</b>.'), 'error')
            return redirect_home()

        return f(*args, **kwargs)

    return decorated_function


def domaintyp_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if kwargs['domaintype'] not in domainlist_title:
            flash(Markup('We don\'t know the domain type <b>' + kwargs['domaintype'] + '</b>.'), 'error')
            return redirect_home()

        return f(*args, **kwargs)

    return decorated_function


# helper functions for decorators

def _get_domainid(kwargs_dict):
    if 'domainid' in kwargs_dict:
        if kwargs_dict['domainid'] <= 0:
            kwargs_dict['domainid'] = current_user.domain_id
            return kwargs_dict['domainid']
        try:
            from ..models.models import Domain
            return Domain.query.filter_by(domain_id=kwargs_dict['domainid']).one().id
        except NoResultFound:
            return 0
    accountid = _get_accountid(kwargs_dict)
    if accountid > 0:
        from ..models.models import User
        return User.query.filter_by(user_id=accountid).one().domain_id
    return 0

def _get_accountid(kwargs_dict):
    if 'accountid' in kwargs_dict:
        if kwargs_dict['accountid'] <= 0:
            kwargs_dict['accountid'] = current_user.domain_id
            return kwargs_dict['accountid']
        try:
            from ..models.models import User
            return User.query.filter_by(user_id=kwargs_dict['accountid']).one().id
        except NoResultFound:
            return  0
    return 0
