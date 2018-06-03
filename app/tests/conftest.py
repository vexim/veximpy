#import datetime
#import json

import pytest
#import pytz
#from mock import Mock

from instance import config
from app.config.settings import sitedomaindefaults, siteadmindefaults, postmasterdefaults, domaindefaults, accountdefaults
from app.app import create_app
from app.app import db as _db
from app.lib.tests import settings as test_settings


#import pdb

from app.models.models import Domain, User

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

    # Create a single user because a lot of tests do not mutate this user.
    # It will result in faster tests.
    
    domain = Domain(**sitedomaindefaults)
    _db.session.add(domain)

    siteadmin = User(**siteadmindefaults)
    siteadmin.password_set(test_settings['TEST_PW_SITEADMIN'])
    _db.session.add(siteadmin)

    domain = Domain(**domaindefaults)
    domain.domain_id = 2
    _db.session.add(domain)

    postmaster = User(**postmasterdefaults)
    postmaster.domain_id = 2
    postmaster.localpart = 'postmaster'
    postmaster.username = 'postmaster@runout.at'
    postmaster.password_set(test_settings['TEST_PW_POSTMASTER'])
    _db.session.add(postmaster)

    user = User(**accountdefaults)
    user.domain_id = 2
    user.localpart = 'user1'
    user.username = 'user1@runout.at'
    user.password_set(test_settings['TEST_PW_USER'])
    _db.session.add(user)

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
