# app/lib/forms_validators.py
"""
Functions:
  Validator Functions for wtforms
"""

#import string
import dns.resolver
import validators
from wtforms import ValidationError
from ..config.settings import settings
from ..models.models import Domain, Domainalia, User


def PasswordRules(form, field):
    """
    Check some rules for passwords
    Password length
    Allowed characters
    """
    if field.data is None:
        return

    if hasattr(form, 'pwd_lengthmin'):
        if len(field.data) < form.pwd_lengthmin.data:
            raise ValidationError('Password too short. Minimum length is 10 characters.')
    elif len(field.data) < form.pwdlengthmin:
        raise ValidationError('Password too short. Minimum length is 10 characters.')

    if not any(_.islower() for _ in field.data):
        raise ValidationError('Password must contain lower case characters, upper case characters, digits and special characters. Allowed characters: ' + form.pwdcharallowed)

    if not any(_.isupper() for _ in field.data):
        raise ValidationError('Password must contain lower case characters, upper case characters, digits and special characters. Allowed characters: ' + form.pwdcharallowed)

    if not any(_.isdigit() for _ in field.data):
        raise ValidationError('Password must contain lower case characters, upper case characters, digits and special characters. Allowed characters: ' + form.pwdcharallowed)

    if not any((not _.isalnum() or _ in settings['PWDCHARSLIG']) for _ in field.data):
        raise ValidationError('Password must contain lower case characters, upper case characters, digits and special characters. Allowed characters: ' + form.pwdcharallowed)

    if any(not (_ in (form.pwdcharallowed)) for _ in field.data):
        raise ValidationError('Password contains illegal characters. Allowed characters: ' + form.pwdcharallowed)

def IPList(form, field):
    """
    IP validator for TextAreaSemicolonSepListField
    which saves values ';' separated
    Check IPv4 and IPv6 syntax
    """
    invalidip = ''
    if field.data:
        for _ in field.data[0].split(';'):
            if not (validators.ip_address.ipv4(_.strip()) or validators.ip_address.ipv6(_.strip())):
                invalidip += _.strip() + ', '
    if invalidip != '':
        raise ValidationError('Invalid IP address: ' + invalidip[:-2])

def URI(form, field):
    """
    Check if the domainname is syntactically valid
    and if an MX record is found
    """
    if field.data is None:
        return
    if (not validators.domain(field.data.strip())) or ('_' in field.data):
        raise ValidationError('Invalid domain name.')
    else:
        try:
            dns.resolver.query(field.data, 'MX')
        except dns.resolver.NXDOMAIN:
            raise ValidationError('No DNS MX record found.')
        except:
            raise ValidationError('DNS error')

def Username(form,  field):
    """
    Check if the given value is a valid username
    It can be an arbitrary string or the localpart@domain from this account
    Checks are not case sensitive
    Check valid characters
    Check if this username is already in username
    
    """

    if field.data is None or field.data == form.localpart.data + '@' + form.domain.domain:
        return
    if '@' in field.data:
        raise ValidationError('Username can not be an eMail address except ' + form.localpart.data + '@' + form.domain.domain)

    Localpart(form,  field)

    if field.data in ('postmaster', 'siteadmin'):
        raise ValidationError('Username ' + field.data + ' is not allowed.')
    UsernameExists(form,  field)

def Localpart(form,  field):
#    import re
    
    if any(not _ in settings['USERNAMES_CHARSALLOWED'] for _ in field.data):
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
        raise ValidationError('Domainname exists')

def UsernameExists(form, field):
    """
    Check if username already exists
    in table users
    """
    if field.data is None:
        return
    if 0 != User.query.filter(User.username==field.data).count():
        raise ValidationError('Account exists')

def LocalpartExists(form, field):
    """
    Check if localpart already exists for actual domain
    in table users
    """
    if field.data is None:
        return
    if 0 != User.query.filter(User.domain_id==form.domain_id.data).filter(User.localpart==field.data).count():
        raise ValidationError('Account exists')

def QuotaDomains(form,  field):
    """
    Check if quotas is <= quotasmax for a domain
    in table users
    """
    if form.quotasmax.data > 0 and form.quotas.data > form.quotasmax.data:
        raise ValidationError('Quotas > Max. Quotas')
    return