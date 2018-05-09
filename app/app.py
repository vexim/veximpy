# app/app.py

from os import listdir,  path
# third-party imports
from flask import abort, Flask, render_template, redirect, request, url_for
from flask_bootstrap import Bootstrap
from flask_login import current_user, LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
#from urllib import urlencode, quote, unquote

# local imports
from config import app_config

# db variable initialization
db = SQLAlchemy()
login_manager = LoginManager()
session_domain_id = 0
session_domainname = ''

def require_siteadmin():
    """
    Prevent non-siteadmins from accessing the page
    """
    if not current_user.is_siteadmin:
        abort(403)

def require_postmaster(domainid):
    """
    Prevent non-postmasters from accessing the page
    """
    if not (current_user.is_postmaster == domainid
            or current_user.is_siteadmin):
        abort(403)

def create_app(config_name):

    global session_domain_id

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    
    Bootstrap(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_message = "You must be logged in to access this page."
    login_manager.login_view = "auth.login"
    migrate = Migrate(app, db)

    session_domain_id = 0

    from app.models import models

    #from .admin import admin as admin_blueprint
    #app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .config import config as config_blueprint
    app.register_blueprint(config_blueprint)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    from .domains import domains as domains_blueprint
    app.register_blueprint(domains_blueprint)

    from .accounts import accounts as accounts_blueprint
    app.register_blueprint(accounts_blueprint)

    @app.template_filter()
    def ressource_dir(d):
        for _ in sorted(listdir(path.join(path.abspath(path.dirname(__file__)), 'static', d)), key=len, reverse=True):
            if _ in request.host:
                return path.join(d, _) + '/'
        
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html', title='Forbidden'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html', title='Page Not Found'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html', title='Server Error'), 500

    return app
