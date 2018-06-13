# app/tests/lib/test_forms_validators.py
# This file is part of veximpy

import pytest
from flask import url_for
from app.lib.tests import assert_status_with_message, assert_status_with_flashmessage, ViewTestMixin
from app.lib.tests_helpers import *
from app.config.tests import settings, responses as tests_responses
from app.config.settings import domaindefaults
from app.lib.forms_validators import *
#import pdb

class TestValidators(ViewTestMixin):

    responses = {
        **tests_responses,
        'DOMAIN_LIST_LOCAL_OK': '>Local Domains</h1',
        'DOMAIN_LIST_ALIAS_OK': '>Alias Domains</h1',
        'DOMAIN_LIST_RELAY_OK': '>Relay Domains</h1',
        'DOMAIN_ADD_SUBMITBUTTON_OK': 'submitadd',
        'DOMAIN_ADD_LOCAL_OK': '>Add local domain</h1>',
        'DOMAIN_ADD_ALIAS_OK': '>Add alias domain</h1>',
        'DOMAIN_ADD_RELAY_OK': '>Add relay domain</h1>',
        'DOMAIN_ADD_LOCAL_POST_OK': 'You have successfully added the domain',
        'DOMAIN_EDIT_SUBMITBUTTON_OK': 'submitedit',
        'DOMAIN_EDIT_LOCAL_OK': '>Edit local domain <b>',
        'DOMAIN_EDIT_ALIAS_OK': '>Edit alias domain <b>',
        'DOMAIN_EDIT_RELAY_OK': '>Edit relay domain <b>',
    }

    def test_validatorsPasswordRules(self):
        form = FormString(**{'x': 'short'})
        with pytest.raises(Exception) as excceptioninfo:
            PasswordRules(form, form.x)
        assert str(excceptioninfo.value) == 'Password too short. Minimum length is 10 characters.'

        form = FormString(**{'x': 'PASSWORD-!12345'})
        with pytest.raises(Exception) as excceptioninfo:
            PasswordRules(form, form.x)
        assert 'lower case' in str(excceptioninfo.value)

        form = FormString(**{'x': 'password-!12345'})
        with pytest.raises(Exception) as excceptioninfo:
            PasswordRules(form, form.x)
        assert 'upper case' in str(excceptioninfo.value)

        form = FormString(**{'x': 'PASSWORD-!password'})
        with pytest.raises(Exception) as excceptioninfo:
            PasswordRules(form, form.x)
        assert 'digits' in str(excceptioninfo.value)

        form = FormString(**{'x': 'PASSWORD12345password'})
        with pytest.raises(Exception) as excceptioninfo:
            PasswordRules(form, form.x)
        assert 'special characters' in str(excceptioninfo.value)

        form = FormString(**{'x': ' "` Passw0rd with illegal Char'})
        with pytest.raises(Exception) as excceptioninfo:
            PasswordRules(form, form.x)
        assert 'Password contains illegal characters.' in str(excceptioninfo.value)

        form = FormString(**{'x': 'vAlId-_ Passw0rd'})
        assert PasswordRules(form, form.x) == None

    def test_validatorsIPList(self):
        form = FormTextAreaSepListField(**{'x': '0.0.0.0 ; xyz'})
        with pytest.raises(Exception) as excceptioninfo:
            IPList(form, form.x)
        assert str(excceptioninfo.value) == 'Invalid IP address: xyz'

        form = FormTextAreaSepListField(**{'x': '666.0.0.0'})
        with pytest.raises(Exception) as excceptioninfo:
            IPList(form, form.x)
        assert str(excceptioninfo.value) == 'Invalid IP address: 666.0.0.0'

        form = FormTextAreaSepListField(**{'x': '127.0.0.1 ; 2001::1'})
        assert IPList(form, form.x) == None

    def test_validatorsURI(self):
        form = FormTextAreaSepListField(**{'x': 'invalid?domain=.name'})
        with pytest.raises(Exception) as excceptioninfo:
            URI(form, form.x)
        assert str(excceptioninfo.value) == 'Invalid domain name.'

        form = FormTextAreaSepListField(**{'x': '000.example.com'})
        with pytest.raises(Exception) as excceptioninfo:
            URI(form, form.x)
        assert str(excceptioninfo.value) == 'No DNS MX record found.'

        form = FormTextAreaSepListField(**{'x': 'runout.at'})
        assert URI(form, form.x) == None

    def test_validatorsUsername(self):
        form = FormString(**{'x': 'test@localpart', 'localpart': 'testlocalpart'})
        form.domain.domain = 'example.com'
        with pytest.raises(Exception) as excceptioninfo:
            Username(form, form.x)
        assert str(excceptioninfo.value) == 'Username can not be an eMail address except ' + form.localpart.data + '@' + form.domain.domain

        form = FormString(**{'x': 'test@example.com', 'localpart': 'testlocalpart'})
        form.domain.domain = 'example.com'
        with pytest.raises(Exception) as excceptioninfo:
            Username(form, form.x)
        assert str(excceptioninfo.value) == 'Username can not be an eMail address except ' + form.localpart.data + '@' + form.domain.domain

        form = FormString(**{'x': 'siteadmin', 'localpart': 'testlocalpart'})
        form.domain.domain = 'example.com'
        with pytest.raises(Exception) as excceptioninfo:
            Username(form, form.x)
        assert str(excceptioninfo.value) == 'Username ' + form.x.data + ' is not allowed.'

        form = FormString(**{'x': 'testusername', 'localpart': 'testlocalpart'})
        form.domain.domain = 'example.com'
        assert Username(form, form.x) == None

        form = FormString(**{'x': 'testlocalpart@example.com', 'localpart': 'testlocalpart'})
        form.domain.domain = 'example.com'
        assert Username(form, form.x) == None

    def test_validatorsLocalpart(self):
        form = FormString(**{'x': 'invalid " localpart'})
        with pytest.raises(Exception) as excceptioninfo:
            Localpart(form, form.x)
        assert str(excceptioninfo.value) == 'Localpart contains illegal characters.'

        form = FormString(**{'x': 'validlocalpart'})
        assert Localpart(form, form.x) == None

    def test_validatorsDomainExists(self):
        form = FormString(**{'x': '02.example.com'})
        with pytest.raises(Exception) as excceptioninfo:
            DomainExists(form, form.x)
        assert str(excceptioninfo.value) == 'Domainname exists.'

        form = FormString(**{'x': 'does-not-exist.example.com'})
        assert DomainExists(form, form.x) == None

    def test_validatorsUsernameExists(self):
        form = FormString(**{'x': 'siteadmin'})
        with pytest.raises(Exception) as excceptioninfo:
            UsernameExists(form, form.x)
        assert str(excceptioninfo.value) == 'Account exists.'

        form = FormString(**{'x': 'does-not-exist-user'})
        assert UsernameExists(form, form.x) == None

    def test_validatorsLocalpartExists(self):
        form = FormString(**{'x': 'siteadmin', 'domain_id': 1})
        with pytest.raises(Exception) as excceptioninfo:
            LocalpartExists(form, form.x)
        assert str(excceptioninfo.value) == 'Account (Localpart) exists.'

        form = FormString(**{'x': 'does-not-exist-localpart', 'domain_id': 1})
        assert LocalpartExists(form, form.x) == None

    def test_validatorsQuotaDomains(self):
        form = FormInteger(**{'x': -1, 'quotas': 2000, 'quotasmax': 1000})
        with pytest.raises(Exception) as excceptioninfo:
            QuotaDomains(form, form.x)
        assert str(excceptioninfo.value) == 'Quotas > Max. Quotas.'

        form = FormInteger(**{'x': -1, 'quotas': 100, 'quotasmax': 1000})
        assert QuotaDomains(form, form.x) == None
        form = FormInteger(**{'x': -1, 'quotas': 1000, 'quotasmax': 0})
        assert QuotaDomains(form, form.x) == None
        
        
        
        
        
        
