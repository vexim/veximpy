# app/tests/auth/test_views.py
# This file is part of veximpy

from app.lib.tests import assert_status_with_message, ViewTestMixin
from app.config.tests import settings, responses as tests_responses

#import pdb

class TestAuth(ViewTestMixin):
    responses = {
        **tests_responses,
        'SITE_LOGIN_OK1': 'Login succeded for user <b>siteadmin</b>',
        'SITE_LOGIN_OK2': '<i class="fa fa-user"></i> siteadmin',
        'POSTMASTER_LOGIN_OK1': 'Login succeded for user <b>postmaster',
        'POSTMASTER_LOGIN_OK2': '<i class="fa fa-user"></i> postmaster',
        'USER_LOGIN_OK1': 'Login succeded for user <b>',
        'USER_LOGIN_OK2': '<i class="fa fa-user"></i> ',
        'LOGIN_FAIL': 'Invalid user or password.',
        'LOGOUT_OK': 'You have successfully been logged out.',
    }

    def test_siteadmin_login(self, db):
        response = self.login(settings['TEST_USER_SITEADMIN'], settings['TEST_PW_SITEADMIN'])
        assert_status_with_message(200, response, self.responses['SITE_LOGIN_OK1'])
        assert_status_with_message(200, response, self.responses['SITE_LOGIN_OK2'])
        self.logout()

        response = self.login(settings['TEST_USER_SITEADMIN'], 'wrong-TEST-password')
        assert_status_with_message(200, response, self.responses['LOGIN_FAIL'])
        self.logout()

        response = self.login('wrong-TEST-user', settings['TEST_PW_SITEADMIN'])
        assert_status_with_message(200, response, self.responses['LOGIN_FAIL'])
        self.logout()

    def test_siteadmin_logout(self, db):
        self.login(settings['TEST_USER_SITEADMIN'], settings['TEST_PW_SITEADMIN'])

        response = self.logout()
        assert_status_with_message(200, response, self.responses['LOGOUT_OK'])

    def test_postmaster_login(self, db):
        response = self.login(settings['TEST_2_USER_POSTMASTER'], settings['TEST_2_PW_POSTMASTER'])
        assert_status_with_message(200, response, self.responses['POSTMASTER_LOGIN_OK1'])
        assert_status_with_message(200, response, self.responses['POSTMASTER_LOGIN_OK2'])
        self.logout()

        response = self.login(settings['TEST_2_USER_POSTMASTER'], 'wrong-TEST-password')
        assert_status_with_message(200, response, self.responses['LOGIN_FAIL'])
        self.logout()

        response = self.login('wrong-TEST-user', settings['TEST_2_PW_POSTMASTER'])
        assert_status_with_message(200, response, self.responses['LOGIN_FAIL'])
        self.logout()

    def test_postmaster_logout(self, db):
        response = self.login(settings['TEST_2_USER_POSTMASTER'], settings['TEST_2_PW_POSTMASTER'])

        response = self.logout()
        assert_status_with_message(200, response, self.responses['LOGOUT_OK'])

    def test_user_login(self, db):
        response = self.login(settings['TEST_2_USER_USER'], settings['TEST_2_PW_USER'])
        assert_status_with_message(200, response, self.responses['USER_LOGIN_OK1'])
        assert_status_with_message(200, response, self.responses['USER_LOGIN_OK2'])
        self.logout()

        response = self.login(settings['TEST_2_USER_USER'], 'wrong-TEST-password')
        assert_status_with_message(200, response, self.responses['LOGIN_FAIL'])
        self.logout()

        response = self.login('wrong-TEST-user', settings['TEST_2_PW_USER'])
        assert_status_with_message(200, response, self.responses['LOGIN_FAIL'])
        self.logout()

    def test_user_logout(self, db):
        self.login(settings['TEST_2_USER_USER'], settings['TEST_2_PW_USER'])

        response = self.logout()
        assert_status_with_message(200, response, self.responses['LOGOUT_OK'])
