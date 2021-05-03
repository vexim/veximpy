# app/lib/forms_validators.py
"""
Functions:
  Validator Functions for wtforms
"""

#import string
import logging
import dns.resolver
import validators
from wtforms import ValidationError
from ..config.settings import settings, domaindefaults
from ..models.models import Domain, Domainalia, User


def PasswordRules(form, field):
    """
    Check some rules for passwords
    Password length
    Allowed characters
    """
    val_msg = []
    val_fail = False

    if field.data is None:
        return

    if hasattr(form, 'pwd_lengthmin'):
        if len(field.data) < form.pwd_lengthmin.data:
            logging.debug('Function PasswordRules. Password too short')
            raise ValidationError('Password too short. Minimum length is 10 characters.')
    elif len(field.data) < form.pwdlengthmin:
        logging.debug('Function PasswordRules. Password too short')
        raise ValidationError('Password too short. Minimum length is 10 characters.')

    if (domaindefaults['pwd_rules'] & settings['PWDRULES_LOWER']):
        val_msg.append('lower case')
        val_fail = val_fail | (not any(_.islower() for _ in field.data))

    if (domaindefaults['pwd_rules'] & settings['PWDRULES_UPPER']):
        val_msg.append('upper case')
        val_fail = val_fail | (not any(_.isupper() for _ in field.data))

    if (domaindefaults['pwd_rules'] & settings['PWDRULES_DIGIT']):
        val_msg.append('digits')
        val_fail = val_fail | (not any(_.isdigit() for _ in field.data))

    if (domaindefaults['pwd_rules'] & settings['PWDRULES_NONALPHA']):
        val_msg.append('special characters')
        val_fail = val_fail | (not any((not _.isalnum() or _ in settings['PWDCHARSLIG']) for _ in field.data))

    if val_fail:
        logging.debug('Function PasswordRules. Missing char group')
        raise ValidationError('Password must contain characters of all of following groups: ' + ', '.join(val_msg) + '.')

    if any(not (_ in (form.pwdcharallowed)) for _ in field.data):
        logging.debug('Function PasswordRules. illegal characters')
        raise ValidationError('Password contains illegal characters. Allowed characters: ' + form.pwdcharallowed)

def IPList(form, field):
    """
    IP validator for TextAreaSemicolonSepListField
    which saves values ';' separated
    Check IPv4 and IPv6 syntax
    """
    invalidip = ''
    if field.data:
        for _ in field.data.split(';'):
            if not (validators.ip_address.ipv4(_.strip()) or validators.ip_address.ipv6(_.strip())):
                invalidip += _.strip() + ', '
#        map(lambda _: 'if not (validators.ip_address.ipv4(_.strip()) or validators.ip_address.ipv6(_.strip())): invalidip += _.strip() + ", "', field.data.split(';'))
    if invalidip != '':
        logging.debug('Function IPList. Invalid IP address')
        raise ValidationError('Invalid IP address: ' + invalidip[:-2])

def URI(form, field):
    """
    Check if the domainname is syntactically valid
    and if an MX record is found
    """
    if field.data is None:
        return
    if (not validators.domain(field.data.strip())) or ('_' in field.data):
        logging.debug('Function URI. Invalid domain name')
        raise ValidationError('Invalid domain name.')
    else:
        try:
            dns.resolver.query(field.data, 'MX')
        except dns.resolver.NXDOMAIN:
            logging.debug('Function URI. No DNS MX record found')
            raise ValidationError('No DNS MX record found.')
        except:
            logging.debug('Function URI. DNS error')
            raise ValidationError('DNS error.')

def Username(form, field):
    """
    Check if the given value is a valid username
    It can be an arbitrary string or the localpart@domain from this account
    Checks are not case sensitive
    Check valid characters
    Check if this username is already in username
    
    """
    if field.data is None or field.data == form.localpart.object_data + '@' + form.domain.domain:
        return
    if '@' in field.data:
        logging.debug('Function Username. Username can not be an eMail address except...')
        raise ValidationError('Username can not be an eMail address except ' + form.localpart.data + '@' + form.domain.domain)

    Localpart(form, field)

    if field.data != 'siteadmin' and form.domain.domain_id == 1:
        logging.debug('Username for siteadmin has to be "siteadmin".')
        raise ValidationError('Username for siteadmin has to be "siteadmin".')

    if (field.data == 'siteadmin' and form.domain.domain_id>1) or field.data in settings['USERNAMES_FORBIDDEN']:
        logging.debug('Function Username. Username not allowed')
        raise ValidationError('Username ' + field.data + ' is not allowed.')
    UsernameExists(form,  field)

def Localpart(form, field):
#    import re
    
    if any(not _ in settings['USERNAMES_CHARSALLOWED'] for _ in field.data):
        logging.debug('Function Localpart. illegal characters')
        raise ValidationError('Localpart contains illegal characters.')

#    if settings('CHECK_RCPT_REMOTE_LOCALPARTS'):
#        """see exim4 CHECK_RCPT_REMOTE_LOCALPARTS macro"""
#        _re = re.compile(settings('CHECK_RCPT_REMOTE_LOCALPARTS'), re.IGNORECASE)
#        if not _re.match(field.data):
#            raise ValidationError('Localpart does not match this regex: ' + settings('CHECK_RCPT_REMOTE_LOCALPARTS'))

def DomainExists(form, field):
    """
    Check if domain already exists
    in 2 tables: domains, domainaliases
    """
    if field.data is None:
        return
    cnt = Domainalia.query.filter(Domainalia.alias==field.data).count()
    cnt += Domain.query.filter(Domain.domain==field.data).count()
    if cnt > 0:
        logging.debug('Function DomainExists. Domainname exists')
        raise ValidationError('Domainname exists.')

def UsernameExists(form, field):
    """
    Check if username already exists
    in table users
    """
    if field.data is None:
        return
    if 0 != User.query.filter(User.username==field.data, User.domain_id!=form.domain.domain_id).count():
        logging.debug('Function UsernameExists. Account exists')
        raise ValidationError('Account exists.')

def LocalpartExists(form, field):
    """
    Check if localpart already exists for actual domain
    in table users
    """
    if field.data is None:
        return
    if 0 != User.query.filter(User.domain_id==form.domain_id.data).filter(User.localpart==field.data).count():
        logging.debug('Function LocalpartExists. Localpart exists')
        raise ValidationError('Account (Localpart) exists.')

def QuotaDomains(form, field):
    """
    Check if quotas is <= quotasmax for a domain
    in table users
    """
    if form.quotasmax.data > 0 and form.quotas.data > form.quotasmax.data:
        logging.debug('Function QuotaDomains. Quotas > Max. Quotas')
        raise ValidationError('Quotas > Max. Quotas.')
    return
