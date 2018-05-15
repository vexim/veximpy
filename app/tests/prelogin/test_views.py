# app/tests/prelogin/test_views.py

from flask import url_for
from app.lib.tests import assert_status_with_message, ViewTestMixin

import pdb

class TestPreLogin(ViewTestMixin):
    def test_rootpage(self, db):
        response = self.client.get(url_for('home.homepage'))
        #pdb.set_trace()
        #assert response.status_code == 200
        assert_status_with_message(200, response, '/login')
        print(response)

    def test_loginpage(self, db):
        response = self.client.get(url_for('auth.login'))
        #pdb.set_trace()
        #assert response.status_code == 200
        assert_status_with_message(200, response, 'Login to your account')

    def test_logoutpage(self, db):
        response = self.client.get(url_for('auth.login'))
        #pdb.set_trace()
        #assert response.status_code == 200
        assert_status_with_message(200, response, 'Login to your account')

#class TestDomain(ViewTestMixin):
#    def test_domain(self, db):
#        response = self.client.get(url_for('auth.login'))
#        #pdb.set_trace()
#        #assert response.status_code == 200
#        assert_status_with_message(200, response, 'Login to your account')
