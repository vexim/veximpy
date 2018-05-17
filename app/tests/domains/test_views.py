# app/tests/domains/test_views.py

from flask import url_for
from app.lib.tests import assert_status_with_message, ViewTestMixin

import pdb

class TestDomains(ViewTestMixin):
    def test_siteadmin_login(self, db):
        response = self.login('siteadmin', 'TEST-password_1657')
        #print(response.data)
        assert_status_with_message(200, response, 'Login succeded for user <b>siteadmin</b>')
        assert_status_with_message(200, response, '<i class="fa fa-user"></i> siteadmin')

        response = self.logout()
        assert_status_with_message(200, response, 'You have successfully been logged out.')
        
        response = self.login('siteadmin', 'wrong-TEST-password')
        assert_status_with_message(200, response, 'Invalid user or password.')

    def test_domainlist(self, db):
        self.login('siteadmin', 'TEST-password_1657')

        response = self.client.get(url_for('domains.domainlist'))
        assert_status_with_message(200, response, '>Local Domains</h1>')
        
        response = self.client.get(url_for('domains.domainlist',  domaintype='local'))
        assert_status_with_message(200, response, '>Local Domains</h1>')
        
        response = self.client.get(url_for('domains.domainlist',  domaintype='alias'))
        assert_status_with_message(200, response, '>Alias Domains</h1>')
        
        response = self.client.get(url_for('domains.domainlist',  domaintype='relay'))
        assert_status_with_message(200, response, '>Relay Domains</h1>')

        response = self.client.get(url_for('domains.domainlist',  domaintype='x-invalid_domaintype-x'))
        assert_status_with_message(200, response, '>Local Domains</h1>')

        self.logout()

    def test_domainadd(self, db):
        self.login('siteadmin', 'TEST-password_1657')

        response = self.client.get(url_for('domains.domains_add'))
        assert_status_with_message(200, response, '>Add Local Domain</h1>')
        assert_status_with_message(200, response, 'submitadd')

        response = self.client.get(url_for('domains.domains_add',  domaintype='local'))
        assert_status_with_message(200, response, '>Add Local Domain</h1>')
        
        response = self.client.get(url_for('domains.domains_add',  domaintype='alias'))
        assert_status_with_message(200, response, '>Add Alias Domain</h1>')
        
        response = self.client.get(url_for('domains.domains_add',  domaintype='relay'))
        assert_status_with_message(200, response, '>Add Relay Domain</h1>')

        response = self.client.get(url_for('domains.domains_add',  domaintype='x-invalid_domaintype-x'))
        assert_status_with_message(200, response, '>Add Local Domain</h1>')

        self.logout()

