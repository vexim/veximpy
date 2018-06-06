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
        d = db.session.query(label('count', func.count(Domain.domain_id))).filter(Domain.is_sitedomain).one()
        if d[0].count != 0:
            print("Sitedomain already exists")
        else:
            domain = Domain(**sitedomaindefaults)
            db.session.add(domain)
            db.session.commit()

        u = db.session.query(label('count', func.count(User.user_id))).filter(User.user_id == 1).all()
        if u[0].count != 0:
            print("Siteadmin user already exists")
        else:
            user = User(**siteadmindefaults)
            user.password_set(siteadmin_password)
            db.session.add(user)
            db.session.commit()

if __name__ == '__main__':
    app.create_siteadmin = create_siteadmin.__get__(app)
    app.create_siteadmin(siteadmin_password=sys.argv[1])
