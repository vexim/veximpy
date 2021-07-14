# app/models/siteadminadd.py
# This file is part of veximpy

import sys, os
from sqlalchemy import func
from sqlalchemy.sql import label
from app.models.models import Domain, User
from app.app import db, create_app
from app.config.settings import sitedomaindefaults, siteadmindefaults

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

# set password for siteadmin
def set_siteadminpassword(password):
    

# create siteadmin user and domain
def create_siteadmin(self, siteadmin_password):
    with app.app_context():
        d = db.session.query(func.count(Domain.domain_id).label('count')).filter(Domain.domain_id == 1).one()
        #print("d.count", d.count)
        if d.count != 0:
            print("Sitedomain already exists")
        else:
            domain = Domain(**sitedomaindefaults)
            db.session.add(domain)
            db.session.commit()

        user = db.session.query(User).filter(User.user_id == 1).one()
        #print("user", user.__dict__)
        if user:
            print("Siteadmin user already exists. Setting new password.")
            user.password_set(siteadmin_password)
            db.session.commit()
        else:
            user = User(**siteadmindefaults)
            print("User", User)
            user.password_set(siteadmin_password)
            db.session.add(user)
            db.session.commit()

if __name__ == '__main__':
    app.create_siteadmin = create_siteadmin.__get__(app)
    app.create_siteadmin(siteadmin_password=sys.argv[1])
