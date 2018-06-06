# app/tests/conftest.py
# This file is part of veximpy

#import datetime
#import json

import pytest
#import pytz
#from mock import Mock

from instance import config
from app.config.settings import sitedomaindefaults, siteadmindefaults, postmasterdefaults, domaindefaults, aliasdomaindefaults, accountdefaults
from app.app import create_app
from app.app import db as _db
from app.config.tests import settings as test_settings


#import pdb

from app.models.models import Domain, Domainalia, User

@pytest.yield_fixture(scope='session')
def app():
    """
    Setup our flask test app, this only gets executed once.

    :return: Flask app
    """
    
    params = {
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': '{0}'.format(config.SQLALCHEMY_DATABASE_URI_TESTS), 
    }

    _app = create_app('tests', settings_override=params)

    # Establish an application context before running the tests.
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.yield_fixture(scope='function')
def client(app):
    """
    Setup an app client, this gets executed for each test function.

    :param app: Pytest fixture
    :return: Flask app client
    """
    yield app.test_client()


@pytest.fixture(scope='session')
def db(app):
    """
    Setup our database, this only gets executed once per session.

    :param app: Pytest fixture
    :return: SQLAlchemy database session
    """
    _db.drop_all()
    _db.create_all()

    # Create site and siteadmin
    domain = Domain(**sitedomaindefaults)
    _db.session.add(domain)

    siteadmin = User(**siteadmindefaults)
    siteadmin.password_set(test_settings['TEST_PW_SITEADMIN'])
    _db.session.add(siteadmin)

    # Create a local domain for testing
    domain = Domain(**domaindefaults)
    domain.domain_id = test_settings['TEST_2_DOMAINID']
    domain.domain = test_settings['TEST_2_DOMAINNAME']
    domain.type = test_settings['TEST_2_DOMAINTYPE']
    _db.session.add(domain)

    postmaster = User(**postmasterdefaults)
    postmaster.domain_id = test_settings['TEST_2_DOMAINID']
    postmaster.localpart = test_settings['TEST_2_POSTMASTER_LOCALPART']
    postmaster.username = test_settings['TEST_2_USER_POSTMASTER']
    postmaster.password_set(test_settings['TEST_2_PW_POSTMASTER'])
    _db.session.add(postmaster)

    user = User(**accountdefaults)
    user.domain_id = test_settings['TEST_2_DOMAINID']
    user.localpart = test_settings['TEST_2_USER_LOCALPART']
    user.username = test_settings['TEST_2_USER_USER']
    user.password_set(test_settings['TEST_2_PW_USER'])
    _db.session.add(user)

    # Create a local domain for testing with alias domain
    domain = Domain(**domaindefaults)
    domain.domain_id = test_settings['TEST_3_DOMAINID']
    domain.domain = test_settings['TEST_3_DOMAINNAME']
    domain.type = test_settings['TEST_3_DOMAINTYPE']
    _db.session.add(domain)

    postmaster = User(**postmasterdefaults)
    postmaster.domain_id = test_settings['TEST_3_DOMAINID']
    postmaster.localpart = test_settings['TEST_3_POSTMASTER_LOCALPART']
    postmaster.username = test_settings['TEST_3_USER_POSTMASTER']
    postmaster.password_set(test_settings['TEST_3_PW_POSTMASTER'])
    _db.session.add(postmaster)

    user = User(**accountdefaults)
    user.domain_id = test_settings['TEST_3_DOMAINID']
    user.localpart = test_settings['TEST_3_USER_LOCALPART']
    user.username = test_settings['TEST_3_USER_USER']
    user.password_set(test_settings['TEST_3_PW_USER'])
    _db.session.add(user)

    domain = Domainalia(**aliasdomaindefaults)
    domain.domainalias_id = test_settings['TEST_3_DOMAINALIASID']
    domain.domain_id = test_settings['TEST_2_DOMAINID']
    domain.alias = test_settings['TEST_3_DOMAINALIASNAME']
    _db.session.add(domain)

    # Create a relay domain for testing
    domain = Domain(**domaindefaults)
    domain.domain_id = test_settings['TEST_4_DOMAINRELAYID']
    domain.type = test_settings['TEST_4_DOMAINTYPE']
    domain.domain = test_settings['TEST_4_DOMAINRELAYNAME']
    _db.session.add(domain)

    _db.session.commit()

    return _db


@pytest.yield_fixture(scope='function')
def session(db):
    """
    Allow very fast tests by using rollbacks and nested sessions. This does
    require that your database supports SQL savepoints, and Postgres does.

    Read more about this at:
    http://stackoverflow.com/a/26624146

    :param db: Pytest fixture
    :return: None
    """
    db.session.begin_nested()

    yield db.session

    db.session.rollback()


@pytest.fixture(scope='session')
def token(db):
    """
    Serialize a JWS token.

    :param db: Pytest fixture
    :return: JWS token
    """
    user = User.find_by_identity('admin@local.host')
    return user.serialize_token()


@pytest.fixture(scope='function')
def users(db):
    """
    Create user fixtures. They reset per test.

    :param db: Pytest fixture
    :return: SQLAlchemy database session
    """
    db.session.query(User).delete()

    users = [
        {
            'role': 'admin',
            'email': 'admin@local.host',
            'password': 'password'
        },
        {
            'active': False,
            'email': 'disabled@local.host',
            'password': 'password'
        }
    ]

    for user in users:
        db.session.add(User(**user))

    db.session.commit()

    return db

#@pytest.yield_fixture(scope='function')
#def domains(db):
#    """
#    Allow very fast tests by using rollbacks and nested sessions. This does
#    require that your database supports SQL savepoints, and Postgres does.
#
#    Read more about this at:
#    http://stackoverflow.com/a/26624146
#
#    :param db: Pytest fixture
#    :return: None
#    """
#
#    domain_dict = {
#        'domain': 'runout.at', 
#        }
#    
#    domain = Domain(**domain_dict)
#    db.session.add(domain)
#    db.session.commit()
#    
#    pdb.set_trace()
#
#    yield db
#
#    #db.session.rollback()
