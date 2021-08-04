# app/lib/forms_validators.py
"""
Functions:
  Validator Functions for wtforms
"""

#import string
import logging
import validators
import re
from dns.resolver import resolve, NXDOMAIN
from dns.exception import DNSException
from wtforms import ValidationError
from ..config.settings import settings, domaindefaults
from ..models.models import Domain, Domainalia, User
from .validators import passwordCheck

def PasswordRules(form, field):
    """
    Check some rules for passwords
    Password length
    Allowed characters
    """

    if field.data:
        checkresult = passwordCheck(field.data, lengthmin=form.pwdlengthmin, charallowed=form.pwdcharallowed)
        logging.debug('passwordCheck: ' + str(checkresult))
        if checkresult:
            logging.debug('passwordCheck: failed.')
            raise ValidationError(checkresult)
    elif form.action == 'add':
        logging.debug('Empty password is not allowed.')
        raise ValidationError('Empty password is not allowed.')


def IPList(form, field):
    """
    IP validator for TextAreaSemicolonSepListField
    which saves values ';' separated
    Check IPv4 and IPv6 syntax
    """
    invalidip = ''
    if field.data:
        for _ in field.data.split(field.separator):
            if not (validators.ip_address.ipv4(_.strip()) or validators.ip_address.ipv6(_.strip())):
                invalidip += _.strip() + ', '
    if invalidip != '':
        logging.debug('Function IPList. Invalid IP address')
        raise ValidationError('Invalid IP address: ' + invalidip[:-2])


def MX(form, field):
    """
    Check if the domainname is syntactically valid
    and if an MX record is found
    """
    if field.data is None:
        return
    if (not validators.domain(field.data.strip())) or ('_' in field.data):
        logging.debug('Function MX. Invalid domain name')
        raise ValidationError('Invalid domain name.')
    else:
        try:
            resolve(field.data, 'MX')
        except NXDOMAIN as e:
            logging.debug('Function MX. No DNS MX record found', e)
            raise ValidationError('No DNS MX record found.')
        except DNSException as e:
            logging.debug('Function MX. DNS error ', e)
            raise ValidationError('DNS error.')

def MailAddressList(form, field):
    """
    eMailAddress validator for TextAreaSemicolonSepListField
    which saves values ',' separated
    Check localpart syntax and domain
    """
    invalidaddr = ''
    localpart_regex = re.compile(
        # dot-atom
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+"
        r"(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*$"
        # quoted-string
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|'
        r"""\\[\001-\011\013\014\016-\177])*"$)""",
        re.IGNORECASE)
    domain_regex = re.compile(
        # domain
        r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
        r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?$)'
        # literal form, ipv4 address (SMTP 4.1.3)
        r'|^\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)'
        r'(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$',
        re.IGNORECASE)
    if field.data:
        for _line in field.data.split(field.separator):

            if not _line or '@' not in _line:
                invalidaddr = _line
            else:
                localpart, domain = _line.rsplit('@', 1)
                
            if not localpart_regex.match(localpart.strip()) or not domain_regex.match(domain.strip()):
                invalidaddr += _line.strip() + ', '
            else:
                try:
                    resolve(domain, 'MX')
                except NXDOMAIN as e:
                        invalidaddr += _line.strip() + ' (No DNS MX record found), '
                except DNSException as e:
                        invalidaddr += _line.strip() + ' (DNS Error), '

    if invalidaddr != '':
        logging.debug('Function MailAddrList. Invalid eMailAddress')
        raise ValidationError('Invalid eMail addresses: ' + invalidaddr[:-2])


def Username(form, field):
    """
    Check if the given value is a valid username
    It can be an arbitrary string or the localpart@domain from this account
    Checks are not case sensitive
    Check valid characters
    Check if this username is already in username
    
    """

    # make sure we do not highjack usernames from other domains
    if field.data is None or field.data == form.localpart.object_data + '@' + form.domain.domain:
        return
    if '@' in field.data:
        logging.debug('Function Username. Username can not be an eMail address except...')
        raise ValidationError('Username can not be an eMail address except ' + form.localpart.data + '@' + form.domain.domain)

    Localpart(form, field)

    # check for not highjacking the siteadmin account
    if field.data != 'siteadmin' and form.domain.domain_id == 1:
        logging.debug('Username for siteadmin has to be "siteadmin".')
        raise ValidationError('Username for siteadmin has to be "siteadmin".')

    # check for special/forbidden usernames
    if (field.data == 'siteadmin' and form.domain.domain_id != 1) or field.data in settings['USERNAMES_FORBIDDEN']:
        logging.debug('Function Username. Username not allowed')
        raise ValidationError('Username ' + field.data + ' is not allowed.')
    UsernameExists(form, field)


def Localpart(form, field):
#    import re
    
    if any(not _ in settings['USERNAMES_CHARSALLOWED'] for _ in field.data):
        logging.debug('Function Localpart. illegal characters')
        raise ValidationError('Localpart contains illegal characters. Allowed characters: ' + form.pwdcharallowed)

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
        logging.debug('Function UsernameExists. Username exists')
        raise ValidationError('Username exists.')

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
