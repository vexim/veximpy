# app/domains/views_domains.py

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
#from wtforms.validators import DataRequired
#from wtforms_alchemy import model_form_factory
from markupsafe import Markup
#from ..config.settings import settings
from .forms_domains import DomainFormLocal, DomainFormAlias, DomainFormRelay, DomainFormMailinglist
from ..accounts.forms_accounts import AccountFormLocal
from . import domains
from ..models.models import Domain, Domainalia, User
from ..app import require_siteadmin,  db

domainlist_title = {'local': 'Local', 'alias': 'Alias', 'relay': 'Relay'}

@domains.route('/domainlist/<domaintype>/')
@domains.route('/domainlist/', defaults={'domaintype': 'local'})
@login_required
def domainlist(domaintype):
    """
    Render the homepage template on the /domains_alias route
    """

    require_siteadmin()

    if domaintype == 'alias':
        domainlist = Domainalia.query.order_by(Domainalia.alias).all()
    else:
        domainlist = Domain.query.filter(Domain.type == domaintype).order_by(Domain.domain)

    return render_template('domains/domainlist.html',
        title="Domains",  list_title=domainlist_title[domaintype] + " Domains",
        domainlist=domainlist,
        domaintype=domaintype)

@domains.route('/domains_enabled/<int:domainid>/<domaintype>/', methods=['GET', 'POST'])
@domains.route('/domains_enabled/',  defaults={'domainid': 0, 'domaintype': 'local'}, methods=['GET', 'POST'])
@login_required
def domains_enabled(domainid, domaintype):
    """
    Render the homepage template on the / route
    """

    require_siteadmin()

    if domaintype == 'alias':
        domain = Domainalia.query.get_or_404(domainid)
    else:
        domain = Domain.query.get_or_404(domainid)

    if domain.enabled == 0 or domain.domain_id == 1:
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
@domains.route('/domains_add/',  defaults={'domaintype': 'local'}, methods=['GET', 'POST'])
@login_required
def domains_add(domaintype):
    """
    Render the homepage template on the / route
    """

    require_siteadmin()

    add_domain = True

    if domaintype == 'local':
        form = DomainFormLocal(action='add')
    elif domaintype == 'alias':
        form = DomainFormAlias(action='add')
        form.domain_id.choices = (Domain.query.with_entities(Domain.domain_id, Domain.domain).filter(Domain.domain_id>1)).filter(Domain.type == 'local').order_by(Domain.domain).all()
    elif domaintype == 'relay':
        form = DomainFormRelay(action='add')
    elif domaintype == 'list':
        form = DomainFormMailinglist(action='add')

    if form.submitcancel.data:
        return redirect(url_for('domains.domainlist', domaintype=domaintype))

    if request.method == 'POST':
        domainname = ''
        if domaintype == 'local':
            domainname = form.domain.data
            domain = Domain()
            account = User()
        elif domaintype == 'alias':
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
                                    title='Add ' + domaintype + ' domain')
            
            if domaintype == 'local':
                account = User()
                form_account = AccountFormLocal(action='addPostmaster',  domain=domain)
                form_account.password1.data = form.password1.data
                form_account.password2.data = form.password2.data
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
                                            title='Add ' + domaintype + ' domain')
                else:
                    flash(Markup('An error occured on adding a postmaster account to domain <b>' + domainname + '</b> during form data validation.'), 'error')
                    return render_template('domains/domain.html', action='Add',
                                            domainname = '', 
                                            add_domain=add_domain, form=form,
                                            title='Add ' + domaintype + 'domain')
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
@domains.route('/domains_edit/',  defaults={'domainid': 0, 'domaintype': 'local'}, methods=['GET', 'POST'])
@login_required
def domains_edit(domainid, domaintype):
    """
    Render the homepage template on the / route
    """

    require_siteadmin()
    add_domain = False

    if domaintype == 'local':
        domain = Domain.query.get_or_404(domainid)
        form = DomainFormLocal(obj=domain, action='edit')
    elif domaintype == 'alias':
        domain = Domainalia.query.get_or_404(domainid)
        form = DomainFormAlias(obj=domain, action='edit')
        form.domain_id.choices = Domain.query.with_entities(Domain.domain_id, Domain.domain).filter(Domain.domain_id>1, Domain.domain!=domain.alias, Domain.type == 'local').order_by(Domain.domain).all()
    elif domaintype == 'relay':
        domain = Domain.query.get_or_404(domainid)
        form = DomainFormRelay(obj=domain, action='edit')
    elif domaintype == 'list':
        domain = Domain.query.get_or_404(domainid)
        form = DomainFormMailinglist(obj=domain, action='edit')

    domainname = domain.domainname

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
@domains.route('/domains_delete/',  defaults={'domainid': 0, 'domaintype': 'local'}, methods=['GET', 'POST'])
@login_required
def domains_delete(domainid, domaintype):
    """
    Render the homepage template on the / route
    """

    require_siteadmin()

    if domaintype == 'alias':
        domain = Domainalia.query.get_or_404(domainid)
    else:
        domain = Domain.query.get_or_404(domainid)

    domainname = domain.domainname

    if domain.enabled == 0 and domain.id>1 and (not domaintype == 'local' or (2>(domain.users.count() | int) and 0==(domain.aliases.count() | int))):
        db.session.delete(domain)
        db.session.commit()
        flash(Markup('You have successfully deleted the domain <b>' + domainname + '</b>.'), 'warning')
    else:
        flash(Markup('You can not delete an enabled domain or a domain having accounts or alises: <b>' + domainname + '</b>.'), 'error')

    # redirect to the domain list
    return redirect(url_for('domains.domainlist', domaintype=domaintype))
    

    return render_template(title="Delete Domainalias")


