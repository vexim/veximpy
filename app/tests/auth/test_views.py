# app/tests/auth/test_views.py

from app.lib.tests import assert_status_with_message, ViewTestMixin
from app.config.tests import settings, responses as tests_responses

#import pdb

class TestAuth(ViewTestMixin):
    responses = {
        **tests_responses,
        'SITE_LOGIN_OK1': 'Login succeded for user <b>siteadmin</b>',
        'SITE_LOGIN_OK2': '<i class="fa fa-user"></i> siteadmin',
        'SITE_LOGIN_FAIL': 'Invalid user or password.',
        'SITE_LOGOUT_OK': 'You have successfully been logged out.',
    }

    def test_siteadmin_login(self, db):
        response = self.login(settings['TEST_USER_SITEADMIN'], settings['TEST_PW_SITEADMIN'])
        #print(response.data)
        assert_status_with_message(200, response, self.responses['SITE_LOGIN_OK1'])
        assert_status_with_message(200, response, self.responses['SITE_LOGIN_OK2'])

        response = self.logout()
        assert_status_with_message(200, response, self.responses['SITE_LOGOUT_OK'])
        
        response = self.login(settings['TEST_USER_SITEADMIN'], 'wrong-TEST-password')
        assert_status_with_message(200, response, self.responses['SITE_LOGIN_FAIL'])

        response = self.login('wrong-TEST-user', settings['TEST_PW_SITEADMIN'])
        assert_status_with_message(200, response, self.responses['SITE_LOGIN_FAIL'])

        self.logout()
