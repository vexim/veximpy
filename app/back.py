# app/back.py
# This snippet is in public domain.
# However, please retain this link in your sources:
# http://flask.pocoo.org/snippets/120/
# Danya Alexeyevsky

from flask import session, redirect, current_app
from .app import app

class back(object):
    """To be used in views.

    Use `anchor` decorator to mark a view as a possible point of return.

    `url()` is the last saved url.

    Use `redirect` to return to the last return point visited.
    """

    cookie = (app.config['REDIRECT_BACK_COOKIE'], 'back')
    default_view = (app.config['REDIRECT_BACK_DEFAULT'], 'index')

    @staticmethod
    def anchor(func, cookie=cookie):
        @functools.wraps(func)
        def result(*args, **kwargs):
            session[cookie] = request.url
            return func(*args, **kwargs)
        return result

    @staticmethod
    def url(default=default_view, cookie=cookie):
        return session.get(cookie, url_for(default))

    @staticmethod
    def redirect(default=default_view, cookie=cookie):
        return redirect(back.url(default, cookie))
back = back()
