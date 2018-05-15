#import datetime
#import json

import pytest
#import pytz
#from mock import Mock

from instance import config
#from app.config.settings import settings
from app.app import create_app
from app.app import db as _db


#import pdb

from app.models.models import Domain, User

@pytest.yield_fixture(scope='session')
def app():
    """
    Setup our flask test app, this only gets executed once.

    :return: Flask app
    """
    
    params = {
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
    
    domain_dict = {
        'domain': 'runout.at',
        'domain_id': 1, 
        }
    
    domain = Domain(**domain_dict)
    _db.session.add(domain)
    _db.session.commit()

    account_dict = {
        'domain_id': 1,
        'role': 0b00001000,
        'localpart': 'postmaster', 
        'username': 'admin@local.host',
    }

    siteadmin = User(**account_dict)
    siteadmin.password_set('password')
    _db.session.add(siteadmin)
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
