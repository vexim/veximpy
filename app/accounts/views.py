# app/accounts/views.py
# This file is part of veximpy

import logging
#from sqlalchemy.sql import or_, and_, tuple_
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy.orm.exc import NoResultFound
from markupsafe import Markup
from .forms import AccountFormLocal, AccountFormAlias #, AccountFormMailinglist
from . import accounts
from ..models.models import Domain, User
from app.app import db
from ..config.settings import settings, accountlist_title
from ..lib.decorators import accountid_check, accounttyp_required, domainid_check, postmaster_required, user_required

#from ..back import back

@accounts.route('/accountlist/<int:domainid>/<accounttype>/')
@accounts.route('/accountlist/<int:domainid>/',  defaults={'accounttype': 'local'})
@accounts.route('/accountlist/',  defaults={'domainid': 0, 'accounttype': 'local'})
@login_required
@postmaster_required
@accounttyp_required
@domainid_check
def accountlist(domainid, accounttype):
    """
    Render the domainlist template on the / route
    """

    if accounttype == 'local':
        accounttype_list = ['local', 'piped']
    else:
        accounttype_list = [accounttype]

    domain = Domain.query.get_or_404(domainid)

    accountlist = (User.query.filter_by(domain_id=domainid)
                             .filter(User.type.in_(accounttype_list)).order_by(User.localpart))

    return render_template('accounts/accountlist.html',
        domainid=domainid,
        title="Accounts", list_title=accountlist_title[accounttype] + " accounts for " + domain.domain,
        postmasterdeleteallow=settings['POSTMASTER_DELETEALLOW'],
        accountlist=accountlist,
        accounttype=accounttype)

@accounts.route('/account_enabled/<int:accountid>/<accounttype>', methods=['GET', 'POST'])
@accounts.route('/account_enabled/',  defaults={'accountid': 0, 'accounttype': 'local'}, methods=['GET', 'POST'])
@login_required
@postmaster_required
@accountid_check
def account_enabled(accountid, accounttype):
    """
    Render the homepage template on the / route
    """

    try:
        account = User.query.filter(User.user_id == accountid).one()
    except NoResultFound:
        flash(Markup('We couldn\'t find the accountid <b>' + str(accountid) + '</b>.'), 'error')
        return redirect(url_for('accounts.accountlist', domainid=account.domain_id, accounttype=accounttype))

    if account.enabled == 0 or account.user_id == 1:
       account.enabled = 1
       enabledtxt = 'enabled'
       flashtype = 'success'
    else:
        account.enabled = 0
        enabledtxt = 'disabled'
        flashtype = 'warning'

    db.session.commit()
    flash(Markup('You have successfully ' + enabledtxt +' the account <b>' + account.username + '</b>.'), flashtype)

    return redirect(url_for('accounts.accountlist', _anchor=accountid, domainid=account.domain_id, accounttype=accounttype))

@accounts.route('/account_add/<int:domainid>/<accounttype>', methods=['GET', 'POST'])
@accounts.route('/account_add/<int:domainid>', defaults={'accounttype': 'local'}, methods=['GET', 'POST'])
@login_required
@postmaster_required
@accounttyp_required
def account_add(domainid, accounttype):
    """
    Render the homepage template on the / route
    """

    add_account = True

    try:
        domain = Domain.query.filter(Domain.domain_id == domainid).one()
    except NoResultFound:
        flash(Markup('We couldn\'t find the domainid <b>' + str(domainid) + '</b>.'), 'error')

    account = User(**domain.get_accountdefaults_dict())

    if accounttype == 'local':
        form = AccountFormLocal(obj=account, action='add', domain=domain)
    elif accounttype == 'alias':
        form = AccountFormAlias(action='add', domain=domain)
    #elif accounttype == 'list':
    #     form = AccountFormMailinglist(action='add', domain=domain)

    #if request.method == 'GET':
        #form.process(MultiDict(domaindefaults))
    accountname = form.username.data

    if request.method == 'POST':
        if form.submitcancel.data:
            return redirect(url_for('accounts.accountlist', domainid=account.domain_id, accounttype=accounttype))

        if form.account_save(account):
            try:
                db.session.add(account)
                db.session.commit()
            except:
                db.session.rollback()
                flash(Markup('Account <b>' + accountname + '</b> already exists.'), 'error')
                return render_template('accounts/account.html', action='Add',
                                    accountname = '', 
                                    add_account=add_account, form=AccountFormLocal(obj=account, action='add', domain=domain),
                                    domainname=domain.domain,
                                    domainid=domainid,
                                    title='Add ' + accounttype + ' account')
        else:
            flash(Markup('An error occured on adding account <b>' + accountname + '</b> during form data validation.'), 'error')
            return render_template('accounts/account.html', action='Add',
                                    accountname = '', 
                                    add_account=add_account, form=AccountFormLocal(obj=account, action='add', domain=domain),
                                    domainname=domain.domain,
                                    domainid=domainid,
                                    title='Add ' + accounttype + ' account')
        flash(Markup('You have successfully added the account <b>' + accountname + '</b>'), 'success')
        return redirect(url_for('accounts.accountlist', domainid=account.domain_id, accounttype=accounttype))
    return render_template('accounts/account.html', action='Add',
                            add_account=add_account, form=form,
                            accountname=accountname,
                            domainname=domain.domain, 
                            domainid=domainid,
                            title='Add ' + accounttype + ' account')

@accounts.route('/account_edit/<int:accountid>/<accounttype>', methods=['GET', 'POST'])
@accounts.route('/account_edit/',  defaults={'accountid': 0, 'accounttype': 'local'}, methods=['GET', 'POST'])
#@user_required
@login_required
@accounttyp_required
def account_edit(accountid, accounttype):
    """
    Render the homepage template on the / route
    """

    add_account = False

    try:
        account = User.query.filter_by(user_id=accountid).one()
        domain = Domain.query.filter_by(domain_id=account.domain_id).one()

        if accounttype == 'local':
            form = AccountFormLocal(obj=account, action='edit',  domain=domain)
            accountname = account.username
    except NoResultFound:
        flash(Markup('We couldn\'t find the accountid <b>' + str(accountid) + '</b>.'), 'error')
        return redirect(url_for('accounts.accountlist', domainid=account.domain_id, _anchor=accountid, accounttype='local'))

    if form.submitcancel.data:
        return redirect(url_for('accounts.accountlist', domainid=account.domain_id, _anchor=accountid, accounttype=accounttype))

    if request.method == 'POST':
        if form.account_save(account):
            try:
                logging.debug(account.__dict__)
                db.session.commit()
                flash(Markup('You have successfully edited the domain <b>' + accountname + '</b>'), 'success')
                # redirect to accountlist page
                return redirect(url_for('accounts.accountlist', domainid=account.domain_id, _anchor=accountid, accounttype=accounttype))
            except:
                db.session.rollback()
                flash(Markup('<b>' + accountname + '</b> name already exists.'), 'error')
                return render_template('domains/domain.html', action='Edit',
                                accountname = accountname, 
                                add_account=add_account, form=form,
                                title='Edit ' + accounttype + 'account')
        else:
            # populate form with readonly data again
            form.localpart.data = account.localpart
            flash(Markup('An error occured on editing account <b>' + accountname + '</b> during form data validation.'), 'error')

    return render_template('accounts/account.html', action='Edit',
                            add_account=add_account, form=form,
                            accountname=accountname,
                            domainname=domain.domain,
                            domainid=account.domain_id, 
                            title='Edit ' + accounttype + ' account')

@accounts.route('/account_delete/<int:accountid>/<accounttype>')
@accounts.route('/account_delete/',  defaults={'accountid': 0, 'accounttype': 'local'}, methods=['GET', 'POST'])
@login_required
@postmaster_required
def account_delete(accountid, accounttype):
    """
    Render the homepage template on the / route
    """

    account = User.query.get_or_404(accountid)

    username = account.username
    domainid = account.domain_id

    if account.is_deleteable:
        db.session.delete(account)
        db.session.commit()
        flash(Markup('You have successfully deleted the account <b>' + username + '</b>.'), 'warning')
    else:
        flash('You can not delete an enabled account, a postmaster or siteadmin: ' + username + '.', 'error')

    # redirect to the domain list
    return redirect(url_for('accounts.accountlist', domainid=domainid, accounttype=accounttype))
    

#    return render_template(title="Delete Domain")
