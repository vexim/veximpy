# app/models/siteadminadd.py
# This file is part of veximpy

import sys, os
from sqlalchemy.sql import label
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from app.models.models import Domain, User
from app.app import db, create_app
from app.config.settings import settings, sitedomaindefaults, siteadmindefaults
from app.lib.validators import passwordCheck

#config_name = os.getenv('FLASK_CONFIG')
#app = create_app(config_name)

# set password for siteadmin
def set_siteadminpassword(app, password, account=None):
    
    pwdchk = passwordCheck(password, lengthmin=settings['PWDLENGTHMIN'], charallowed=settings['PWDCHARSALLOWED'])
    if pwdchk:
        print(pwdchk)
        return

    with app.app_context():
        if not account:
            try:
                account = db.session.query(User).filter(User.user_id == 1).one()
            except NoResultFound as e:
                print('Siteadmin does not exist. Can not set password for missing account. ', e)
                return False

        account.password_set(password)
        db.session.commit()

        return account

def create_sitedomain(app):
    with app.app_context():
        try:
            domain = db.session.query(Domain).filter(Domain.domain_id == 1).one()
            print("Sitedomain already exists")
        except NoResultFound as e:
            print('Creating sitedomain.')
            domain = Domain(**sitedomaindefaults)
            db.session.add(domain)
            db.session.commit()

    
# create siteadmin user and domain
def create_siteadmin(app, siteadmin_password):
    pwdchk = passwordCheck(password, lengthmin=settings['PWDLENGTHMIN'], charallowed=settings['PWDCHARSALLOWED'])
    if pwdchk:
        print(pwdchk)
        return

    with app.app_context():
        try:
            account = db.session.query(User).filter(User.user_id == 1).one()
            print("Siteadmin user already exists. Setting new password.")
            account.password_set(siteadmin_password)
            db.session.commit()
        except NoResultFound as e:
            print('Creating siteadmin with provided password.')
            account = User(**siteadmindefaults)
            account.password_set(siteadmin_password)
            db.session.add(account)
            db.session.commit()
