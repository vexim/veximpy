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

# create siteadmin user and domain
def create_siteadmin(self, siteadmin_password):
    with app.app_context():
        d = db.session.query(func.count(Domain.domain_id).label('count')).filter(Domain.domain_id == 1).one()
        print("d.count", d.count)
        if d.count != 0:
            print("Sitedomain already exists")
        else:
            domain = Domain(**sitedomaindefaults)
            db.session.add(domain)
            db.session.commit()

        u = db.session.query(func.count(User.user_id).label('count')).filter(User.user_id == 1).one()
        print("u.count", u.count)
        if u.count != 0:
            print("Siteadmin user already exists")
        else:
            user = User(**siteadmindefaults)
            print("User", User)
            user.password_set(siteadmin_password)
            db.session.add(user)
            db.session.commit()

if __name__ == '__main__':
    app.create_siteadmin = create_siteadmin.__get__(app)
    app.create_siteadmin(siteadmin_password=sys.argv[1])
