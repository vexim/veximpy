# app/tests/domains/test_views.py

from flask import url_for
from app.lib.tests import assert_status_with_message, ViewTestMixin
from app.config.tests import settings, responses as tests_responses

#import pdb

class TestDomains(ViewTestMixin):
    responses = {
        **tests_responses,
        'DOMAIN_LIST_LOCAL_OK': '>Local Domains</h1',
        'DOMAIN_LIST_ALIAS_OK': '>Alias Domains</h1',
        'DOMAIN_LIST_RELAY_OK': '>Relay Domains</h1',
        'DOMAIN_ADD_SUBMITBUTTON_OK': 'submitadd',
        'DOMAIN_ADD_LOCAL_OK': '>Add local domain</h1>',
        'DOMAIN_ADD_ALIAS_OK': '>Add alias domain</h1>',
        'DOMAIN_ADD_RELAY_OK': '>Add relay domain</h1>',
        'DOMAIN_EDIT_SUBMITBUTTON_OK': 'submitedit',
        'DOMAIN_EDIT_LOCAL_OK': '>Edit local domain <b>',
        'DOMAIN_EDIT_ALIAS_OK': '>Edit alias domain <b>',
        'DOMAIN_EDIT_RELAY_OK': '>Edit relay domain <b>',
    }

    def test_localdomainlist(self, db):
        self.login(settings['TEST_USER_SITEADMIN'], settings['TEST_PW_SITEADMIN'])

        response = self.client.get(url_for('domains.domainlist'))
        assert_status_with_message(200, response, self.responses['DOMAIN_LIST_LOCAL_OK'])

        response = self.client.get(url_for('domains.domainlist', domaintype='local'))
        assert_status_with_message(200, response, self.responses['DOMAIN_LIST_LOCAL_OK'])

        response = self.client.get(url_for('domains.domainlist', domaintype='x-invalid_domaintype-x'))
        assert_status_with_message(200, response, self.responses['DOMAIN_LIST_LOCAL_OK'])

        self.logout()

    def test_aliasdomainlist(self, db):
        self.login(settings['TEST_USER_SITEADMIN'], settings['TEST_PW_SITEADMIN'])

        response = self.client.get(url_for('domains.domainlist',  domaintype='alias'))
        assert_status_with_message(200, response, self.responses['DOMAIN_LIST_ALIAS_OK'])

        self.logout()

    def test_relaydomainlist(self, db):
        self.login(settings['TEST_USER_SITEADMIN'], settings['TEST_PW_SITEADMIN'])

        response = self.client.get(url_for('domains.domainlist', domaintype='relay'))
        assert_status_with_message(200, response, self.responses['DOMAIN_LIST_RELAY_OK'])

        self.logout()

    def test_localdomainadd(self, db):
        self.login(settings['TEST_USER_SITEADMIN'], settings['TEST_PW_SITEADMIN'])

        response = self.client.get(url_for('domains.domains_add'))
        assert_status_with_message(200, response, self.responses['DOMAIN_ADD_LOCAL_OK'])
        assert_status_with_message(200, response, self.responses['DOMAIN_ADD_SUBMITBUTTON_OK'])

        response = self.client.get(url_for('domains.domains_add', domaintype='local'))
        assert_status_with_message(200, response, self.responses['DOMAIN_ADD_LOCAL_OK'])

        response = self.client.get(url_for('domains.domains_add', domaintype='x-invalid_domaintype-x'))
        assert_status_with_message(200, response, self.responses['DOMAIN_ADD_LOCAL_OK'])

        self.logout()

    def test_aliasdomainadd(self, db):
        self.login(settings['TEST_USER_SITEADMIN'], settings['TEST_PW_SITEADMIN'])

        response = self.client.get(url_for('domains.domains_add', domaintype='alias'))
        assert_status_with_message(200, response, self.responses['DOMAIN_ADD_ALIAS_OK'])

        self.logout()

    def test_relaydomainadd(self, db):
        self.login(settings['TEST_USER_SITEADMIN'], settings['TEST_PW_SITEADMIN'])

        response = self.client.get(url_for('domains.domains_add', domaintype='relay'))
        assert_status_with_message(200, response, self.responses['DOMAIN_ADD_RELAY_OK'])

        self.logout()

    def test_localdomainedit(self, db):
        self.login(settings['TEST_USER_SITEADMIN'], settings['TEST_PW_SITEADMIN'])

#        response = self.client.get(url_for('domains.domains_edit'))
#        assert_status_with_message(404, response, self.responses['404'])
#
#        response = self.client.get(url_for('domains.domains_edit', domainid=2))
#        assert_status_with_message(404, response, self.responses['404'])

        response = self.client.get(url_for('domains.domains_edit', domainid=2, domaintype='local'))
        assert_status_with_message(200, response, self.responses['DOMAIN_EDIT_LOCAL_OK'])
        assert_status_with_message(200, response, self.responses['DOMAIN_EDIT_SUBMITBUTTON_OK'])

        response = self.client.get(url_for('domains.domains_edit', domainid=-1, domaintype='local'))
        assert_status_with_message(404, response, self.responses['404'])

        response = self.client.get(url_for('domains.domains_edit', domainid=2, domaintype='x-invalid_domaintype-x'))
        assert_status_with_message(302, response, self.responses['302'])

        self.logout()

#    def test_aliasdomainedit(self, db):
#        self.login(settings['TEST_USER_SITEADMIN'], settings['TEST_PW_SITEADMIN'])
#
#        response = self.client.get(url_for('domains.domains_edit', domainid=2, domaintype='alias'))
#        assert_status_with_message(200, response, self.responses['DOMAIN_EDIT_ALIAS_OK'])
#
#        self.logout()
#
#    def test_relaydomainedit(self, db):
#        self.login(settings['TEST_USER_SITEADMIN'], settings['TEST_PW_SITEADMIN'])
#
#        response = self.client.get(url_for('domains.domains_edit', domainid=2, domaintype='relay'))
#        assert_status_with_message(200, response, self.responses['DOMAIN_EDIT_RELAY_OK'])
#
#        self.logout()
