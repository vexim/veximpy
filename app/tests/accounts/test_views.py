# app/tests/domains/test_views.py

from flask import url_for
from app.lib.tests import assert_status_with_message, ViewTestMixin, settings

#import pdb

class TestAccounts(ViewTestMixin):
    def test_localaccountadd(self, db):
        self.login('siteadmin', settings['TEST_PW_SITEADMIN'])

        response = self.client.get(url_for('accounts.account_add', domainid=2))
        assert_status_with_message(200, response, '>Add Account</h1>')
        assert_status_with_message(200, response, 'submitadd')

        response = self.client.get(url_for('accounts.account_add', domainid=2, accounttype='local'))
        assert_status_with_message(200, response, '>Add Account</h1>')

        response = self.client.get(url_for('accounts.account_add', domainid=2, accounttype='x-invalid-x'))
        assert_status_with_message(302, response, '')

        response = self.client.get(url_for('accounts.account_add', domainid=-1, accounttype='local'))
        assert_status_with_message(404, response, '> 404 Error <')

        self.logout()

#    def test_aliasdomainadd(self, db):
#        self.login('siteadmin', settings['TEST_PW_SITEADMIN'])
#
#        response = self.client.get(url_for('accounts.account_add', domainid=2, accounttype='alias'))
#        assert_status_with_message(200, response, '>Add Alias Account</h1>')
#
#    def test_relaydomainadd(self, db):
#        self.login('siteadmin', settings['TEST_PW_SITEADMIN'])
#
#        response = self.client.get(url_for('accounts.account_add', domainid=2, accounttype='list'))
#        assert_status_with_message(200, response, '>Add Relay Account</h1>')
#
#        self.logout()

