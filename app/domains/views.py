# app/domains/views.py
# This file is part of veximpy

import logging
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from flask_wtf.csrf import generate_csrf
from sqlalchemy.orm.exc import NoResultFound
#from wtforms.validators import DataRequired
#from wtforms_alchemy import model_form_factory
#from werkzeug import MultiDict
from markupsafe import Markup
from .forms import DomainFormLocal, DomainFormAlias, DomainFormRelay, DomainFormMailinglist
from ..accounts.forms import AccountFormLocal
from . import domains
from ..models.models import Domain, Domainalia, User
from ..app import db
from ..config.settings import domaindefaults, aliasdomaindefaults, domainlist_title
from ..lib.decorators import domainid_check, domaintyp_required, siteadmin_required

@domains.route('/domainlist/<domaintype>/')
@domains.route('/domainlist/', defaults={'domaintype': 'local'})
@login_required
@siteadmin_required
@domaintyp_required
def domainlist(domaintype):
    """
    Render the homepage template on the /domains_alias route
    """

    if domaintype == 'alias':
        domainlist = Domainalia.query.order_by(Domainalia.alias).all()
    else:
        domainlist = Domain.query.filter(Domain.type == domaintype).order_by(Domain.domain)

    return render_template('domains/domainlist.html',
        title="Domains", list_title=domainlist_title[domaintype] + " Domains",
        domainlist=domainlist,
        domaintype=domaintype)

@domains.route('/domains_enabled/<int:domainid>/<domaintype>/', methods=['GET', 'POST'])
@domains.route('/domains_enabled/', defaults={'domainid': 0, 'domaintype': 'local'}, methods=['GET', 'POST'])
@login_required
@siteadmin_required
@domainid_check
def domains_enabled(domainid, domaintype):
    """
    Render the homepage template on the / route
    """

    try:
        if domaintype == 'alias':
            domain = Domainalia.query.filter(Domainalia.domainalias_id == domainid).one()
        else:
            domain = Domain.query.filter(Domain.domain_id == domainid).one()
    except NoResultFound:
        flash(Markup('We couldn\'t find the domainid <b>' + str(domainid) + '</b>.'), 'error')
        return redirect(url_for('domains.domainlist', domaintype='local'))

    if domain.is_sitedomain or domain.enabled == 0:
       domain.enabled = 1
       enabledtxt = 'enabled'
       flashtype = 'success'
    else:
        domain.enabled = 0
        enabledtxt = 'disabled'
        flashtype = 'warning'
    db.session.commit()
    flash(Markup('You have successfully ' + enabledtxt +' the domain <b>' + domain.domainname + '</b>.'), flashtype)

    return redirect(url_for('domains.domainlist', _anchor=domainid, domaintype=domaintype))

@domains.route('/domains_add/<domaintype>', methods=['GET', 'POST'])
@domains.route('/domains_add/', defaults={'domaintype': 'local'}, methods=['GET', 'POST'])
@login_required
@siteadmin_required
@domaintyp_required
def domains_add(domaintype):
    """
    Render the homepage template on the / route
    """

    add_domain = True

    if domaintype == 'local':
        form = DomainFormLocal(obj=Domain(**domaindefaults), action='add')
        #form.process(**domaindefaults)
    elif domaintype == 'alias':
        domain_id_available = (Domain.query.with_entities(Domain.domain_id, Domain.domain).filter(Domain.domain_id>1)).filter(Domain.type == 'local').order_by(Domain.domain).all()
        domain_id_list = [(_.domain_id, _.domain) for _ in domain_id_available]
        form = DomainFormAlias(obj=Domainalia(**aliasdomaindefaults), action='add')
        form.domain_id.choices = domain_id_list
        #form.process(**aliasdomaindefaults)
    elif domaintype == 'relay':
        form = DomainFormRelay(obj=Domain(**domaindefaults), action='add')
        #form.process(**domaindefaults)
    elif domaintype == 'list':
        form = DomainFormMailinglist(obj=Domain(**domaindefaults), action='add')
        #form.process(**domaindefaults)


#    if form and request.method == 'GET':
#        form.process(MultiDict(domaindefaults))

    if form.submitcancel.data:
        return redirect(url_for('domains.domainlist', domaintype=domaintype))

    if request.method == 'POST':
        domainname = ''
        if domaintype == 'alias':
            domainname = form.alias.data
            domain = Domainalia()
        else:
            domainname = form.domain.data
            domain = Domain()

        #        elif domaintype == 'list':
        #            is_mailinglist = 1
        #            form = DomainFormMailinglist()

        if form.domain_save(domain):
            try:
                # add domain to the database
                db.session.add(domain)
                db.session.commit()
            except:
                # in case domain name already exists
                db.session.rollback()
                flash(Markup('Domain <b>' + domainname + '</b> already exists.'), 'error')
                return render_template('domains/domain.html', action='Add',
                                    domainname = '', 
                                    add_domain=add_domain, form=form,
                                    title='Add ' + domaintype + ' Domain')
            
            if domaintype == 'local':
                # add postmaster account
                account = User(**domain.get_postmasterdefaults_dict())
                form_account = AccountFormLocal(obj=account, action='addPostmaster', domain=domain)
                print(account.__dict__)
                form_account.process(**{**domain.get_postmasterdefaults_dict(), 'password1': form.password1.data, 'csrf_token': generate_csrf()})
                #form_account.password1.data = form.password1.data
                #form_account.password2.data = form.password2.data
                if form_account.account_save(account):
                    try:
                        db.session.add(account)
                        db.session.commit()
                    except:
                        db.session.rollback()
                        flash(Markup('Postmaster account for <b>' + domainname + '</b> name already exists.'), 'error')
                        return render_template('domains/domain.html', action='Add',
                                            domainname = '', 
                                            add_domain=add_domain, form=form,
                                            title='Add ' + domaintype + ' Domain')
                else:
                    logging.debug(form_account.errors)
                    flash(Markup('An error occured on adding a postmaster account to domain <b>' + domainname + '</b> during form data validation.'), 'error')
                    return render_template('domains/domain.html', action='Add',
                                            domainname = '', 
                                            add_domain=add_domain, form=form,
                                            title='Add ' + domaintype + ' Domain')

#                    return render_template('accounts/account.html', action='Add',
#                                    accountname = '', 
#                                    add_account=True, form=AccountFormLocal(obj=account, action='add', domain=domain),
#                                    domainname=domain.domain,
#                                    domainid=domain.id, 
#                                    title='Add ' + 'local' + ' account')





            flash(Markup('You have successfully added the domain <b>' + domainname + '</b>'), 'success')

            # redirect to domainlist page
            return redirect(url_for('domains.domainlist', _anchor=domain.id, domaintype=domaintype))
        else:
            flash(Markup('An error occured on adding domain <b>' + domainname + '</b> during form data validation.'), 'error')

    # load domain template
    return render_template('domains/domain.html', action='Add',
                            domainname = '', 
                            add_domain=add_domain, form=form,
                            title='Add ' + domaintype + ' domain')

@domains.route('/domains_edit/<int:domainid>/<domaintype>/', methods=['GET', 'POST'])
#@domains.route('/domains_edit/', defaults={'domainid': 0, 'domaintype': 'local'}, methods=['GET', 'POST'])
@login_required
@siteadmin_required
@domaintyp_required
@domainid_check
def domains_edit(domainid, domaintype):
    """
    Render the homepage template on the / route
    """

    add_domain = False

    # create DB object for domain
    try:
        if domaintype == 'alias':
            domain = Domainalia.query.filter_by(domainalias_id=domainid).one()
        else:
            domain = Domain.query.filter_by(domain_id=domainid).one()
        domainname = domain.domainname
    except NoResultFound:
        flash(Markup('We couldn\'t find the domainid <b>' + str(domainid) + '</b>.'), 'error')
        return redirect(url_for('domains.domainlist', domaintype='local'))

    # create forms
    if domaintype == 'local':
        form = DomainFormLocal(obj=domain, action='edit')
    elif domaintype == 'alias':
        form = DomainFormAlias(obj=domain, action='edit')
        form.domain_id.choices = Domain.query.with_entities(Domain.domain_id, Domain.domain).filter(Domain.domain_id>1, Domain.domain!=domain.alias, Domain.type == 'local').order_by(Domain.domain).all()
    elif domaintype == 'relay':
        form = DomainFormRelay(obj=domain, action='edit')
    elif domaintype == 'list':
        form = DomainFormMailinglist(obj=domain, action='edit')

    if form.submitcancel.data:
        return redirect(url_for('domains.domainlist', _anchor=domainid, domaintype=domaintype))

    if request.method == 'POST':
        if form.domain_save(domain):
            try:
                db.session.commit()
                flash(Markup('You have successfully edited the domain <b>' + domainname + '</b>'), 'success')
                # redirect to domainlist page
                return redirect(url_for('domains.domainlist', _anchor=domainid, domaintype=domaintype))
            except:
                db.session.rollback()
                flash(Markup('<b>' + domainname + '</b> name already exists.'), 'error')
                return render_template('domains/domain.html', action='Edit',
                                domainname = domainname, 
                                add_domain=add_domain, form=form,
                                title='Edit ' + domaintype + 'domain')
        else:
            # populate form with readonly data again
            form.domain.data = domain.domain
            form.maildir.data = domain.maildir
            flash(Markup('An error occured on editing domain <b>' + domainname + '</b> during form data validation.'), 'error')

    return render_template('domains/domain.html', action='Edit',
                            domainname=domainname, 
                            add_domain=add_domain, form=form,
                            title='Edit ' + domaintype + ' domain')


@domains.route('/domains_delete/<int:domainid>/<domaintype>/', methods=['GET', 'POST'])
@domains.route('/domains_delete/', defaults={'domainid': 0, 'domaintype': 'local'}, methods=['GET', 'POST'])
@login_required
@siteadmin_required
@domaintyp_required
@domainid_check
def domains_delete(domainid, domaintype):
    """
    Render the homepage template on the / route
    """

    if domaintype == 'alias':
        domain = Domainalia.query.get_or_404(domainid)
    else:
        domain = Domain.query.get_or_404(domainid)

    domainname = domain.domainname

    if domain.is_deleteable:
        db.session.delete(domain)
        db.session.commit()
        flash(Markup('You have successfully deleted the domain <b>' + domainname + '</b>.'), 'warning')
    else:
        flash(Markup('You can not delete an enabled domain or a domain having accounts or alises: <b>' + domainname + '</b>.'), 'error')

    # redirect to the domain list
    return redirect(url_for('domains.domainlist', domaintype=domaintype))
    

    return render_template(title="Delete Domainalias")


