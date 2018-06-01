# app/accounts/views.py

#import sys
#from sqlalchemy.sql import or_, and_, tuple_
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import login_required
from markupsafe import Markup
from .forms import AccountFormLocal
from . import accounts
from ..models.models import Domain, User
from app.app import require_postmaster, db, session_domain_id
from ..config.settings import settings

#from ..back import back

accountlist_title = {'local': 'Local', 'alias': 'Alias', 'list': 'Mailinglist'}

def domain_name2id(domainname):
    d = Domain.query.filter_by(domain=domainname)
    return d.id

@accounts.route('/accountlist/<int:domainid>/<accounttype>/')
@accounts.route('/accountlist/<int:domainid>/',  defaults={'accounttype': 'local'})
@accounts.route('/accountlist/',  defaults={'domainid': 0, 'accounttype': 'local'})
@login_required
def accountlist(domainid, accounttype):
    """
    Render the domainlist template on the / route
    """

    require_postmaster(domainid)

    if accounttype == 'local':
        accounttype_list = ['local',  'piped']
    else:
        accounttype_list = [accounttype]

    if domainid < 1:
        domainid = session_domain_id
        if session_domain_id < 1:
            abort(404)
    domain = Domain.query.filter_by(domain_id=domainid).one()

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
def account_enabled(accountid, accounttype):
    """
    Render the homepage template on the / route
    """

    account = User.query.get_or_404(accountid)
    #domain = Domain.query.get_or_404(account.domain_id)
    require_postmaster(account.domain_id)

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
def account_add(domainid, accounttype):
    """
    Render the homepage template on the / route
    """

    add_account = True

    require_postmaster(domainid)

    domain = Domain.query.get_or_404(domainid)
    account = User()

    if accounttype == 'local':
        form = AccountFormLocal(action='add', domain=domain)

    accountname = form.username.data
    if request.method == 'POST':
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
    return render_template('accounts/account.html', action='Add',
                            add_account=add_account, form=form,
                            accountname=accountname,
                            domainname=domain.domain, 
                            domainid=domainid,
                            title='Add ' + accounttype + ' account')

@accounts.route('/account_edit/<int:accountid>/<accounttype>', methods=['GET', 'POST'])
@accounts.route('/account_edit/',  defaults={'accountid': 0, 'accounttype': 'local'}, methods=['GET', 'POST'])
@login_required
def account_edit(accountid, accounttype):
    """
    Render the homepage template on the / route
    """

    add_account = False

    account = User.query.get_or_404(accountid)
    domain = Domain.query.get_or_404(account.domain_id)

    if accounttype == 'local':
        form = AccountFormLocal(obj=account, action='edit',  domain=domain)

    accountname = account.username

    return render_template('accounts/account.html', action='Edit',
                            add_account=add_account, form=form,
                            accountname=accountname,
                            domainname=domain.domain,
                            domainid=account.domain_id, 
                            title='Edit ' + accounttype + ' account')

@accounts.route('/account_delete/<int:accountid>/<accounttype>')
@accounts.route('/account_delete/',  defaults={'accountid': 0, 'accounttype': 'local'}, methods=['GET', 'POST'])
@login_required
def account_delete(accountid, accounttype):
    """
    Render the homepage template on the / route
    """

    account = User.query.get_or_404(accountid)
    require_postmaster(account.domain_id)

    username = account.username
    domainid = account.domain_id

    if account.enabled == 0 and account.id > 1 and (not account.is_postmaster or settings['POSTMASTER_DELETEALLOW'] == 1):
        db.session.delete(account)
        db.session.commit()
        flash(Markup('You have successfully deleted the account <b>' + username + '</b>.'), 'warning')
    else:
        flash('You can not delete an enabled account, a postmaster or siteadmin: ' + username + '.', 'error')

    # redirect to the domain list
    return redirect(url_for('accounts.accountlist', domainid=domainid, accounttype=accounttype))
    

#    return render_template(title="Delete Domain")
