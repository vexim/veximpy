# config.py

import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    """
    Common configurations
    """

    # Put any configurations here that are common across all environments

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """
    Development configurations
    """

    DEBUG = 1
    #TESTING = True
    #SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SERVER_NAME = 'veximpy.runout.at'


class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False


class TestsConfig(Config):
    """
    Tests configurations
    for running automated tests
    """

    DEBUG = 1
    TESTING = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SERVER_NAME = 'veximpy.runout.at'


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'tests': TestsConfig,
}
