# app/tests/accounts/test_views.py

from flask import url_for
from app.lib.tests import assert_status_with_message, assert_status_with_flashmessage, ViewTestMixin
from app.config.tests import settings, responses as tests_responses

import pdb

class TestAccounts(ViewTestMixin):
    responses = {
        **tests_responses,
        'ACCOUNT_LIST_LOCAL_OK': '>Local accounts for ',
        'ACCOUNT_LIST_ALIAS_OK': '>Alias accounts for ',
        'ACCOUNT_LIST_LIST_OK': '>Mailinglist accounts for ',
        'ACCOUNT_ADD_SUBMITBUTTON_OK': 'submitadd',
        'ACCOUNT_ADD_LOCAL_OK': '>Add local account</h1>',
        'ACCOUNT_ADD_ALIAS_OK': '>Add alias account</h1>',
        'ACCOUNT_ADD_RELAY_OK': '>Add mailinglist account</h1>',
        'ACCOUNT_EDIT_SUBMITBUTTON_OK': 'submitedit',
        'ACCOUNT_EDIT_LOCAL_OK': '>Edit local account <b>',
        'ACCOUNT_EDIT_ALIAS_OK': '>Edit alias account <b>',
        'ACCOUNT_EDIT_RELAY_OK': '>Edit mailinglist account <b>',
    }

    def test_localaccountlist(self, db):
        self.login(settings['TEST_USER_SITEADMIN'], settings['TEST_PW_SITEADMIN'])

        response = self.client.get(url_for('accounts.accountlist', domainid=2))
        assert_status_with_message(200, response, self.responses['ACCOUNT_LIST_LOCAL_OK'])
        
        response = self.client.get(url_for('accounts.accountlist', domainid=2, accounttype='local'))
        assert_status_with_message(200, response, self.responses['ACCOUNT_LIST_LOCAL_OK'])

        response = self.client.get(url_for('accounts.accountlist', domainid=2, accounttype='x-invalid_domaintype-x'))
        assert_status_with_message(302, response, self.responses['302'])

        self.logout()

        # as user
        self.login(settings['TEST_2_USER_USER'], settings['TEST_2_PW_USER'])

        response = self.client.get(url_for('accounts.accountlist', domainid=2, accounttype='local'))
        assert_status_with_flashmessage(302, response, self.client, self.responses['POSTMASTER_REQUIRED'], 'error')

        self.logout()

        # as postmaster
        self.login(settings['TEST_2_USER_POSTMASTER'], settings['TEST_2_PW_POSTMASTER'])

        response = self.client.get(url_for('accounts.accountlist', domainid=2, accounttype='local'))
        assert_status_with_message(200, response, self.responses['ACCOUNT_LIST_LOCAL_OK'])

        self.logout()

    def test_aliasaccountlist(self, db):
        self.login(settings['TEST_USER_SITEADMIN'], settings['TEST_PW_SITEADMIN'])

        response = self.client.get(url_for('accounts.accountlist', domainid=2,  accounttype='alias'))
        #pdb.set_trace()
        assert_status_with_message(200, response, self.responses['ACCOUNT_LIST_ALIAS_OK'])

        self.logout()

#    def test_listaccountlist(self, db):
#        self.login(settings['TEST_USER_SITEADMIN'], settings['TEST_PW_SITEADMIN'])
#
#        response = self.client.get(url_for('accounts.accountlist', domainid=2, domaintype='list'))
#        assert_status_with_message(200, response, self.responses['DOMAIN_LIST_LIST_OK'])
#
#        self.logout()

    def test_localaccountadd(self, db):
        self.login(settings['TEST_USER_SITEADMIN'], settings['TEST_PW_SITEADMIN'])

        response = self.client.get(url_for('accounts.account_add', domainid=2))
        assert_status_with_message(200, response, self.responses['ACCOUNT_ADD_LOCAL_OK'])
        assert_status_with_message(200, response, 'submitadd')

        response = self.client.get(url_for('accounts.account_add', domainid=2, accounttype='local'))
        assert_status_with_message(200, response, self.responses['ACCOUNT_ADD_LOCAL_OK'])

        response = self.client.get(url_for('accounts.account_add', domainid=2, accounttype='x-invalid-x'))
        assert_status_with_message(302, response, self.responses['302'])

        response = self.client.get(url_for('accounts.account_add', domainid=-1, accounttype='local'))
        assert_status_with_message(404, response, self.responses['404'])

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

