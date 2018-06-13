# app/lib/defaults_functions.py
# This file is part of veximpy

from ..config.settings import domaindefaults, accountdefaults, postmasterdefaults

def get_accountdefaults(domain):
    _defaults = {
        **accountdefaults, 
        'domain_id': domain.id,
        'enabled': domaindefaults['enabled'],
        'uid': domain.uid,
        'gid': domain.gid,
        'smtp': domain.maildir,
        'quota': domain.quotas,
        'maxmsgsize': domain.maxmsgsize,
        'on_avscan': domain.avscan,
        'on_spamassassin': domain.spamassassin,
        'sa_tag': domain.sa_tag,
        'sa_refuse': domain.sa_refuse,
    }
    return _defaults

def get_postmasterdefaults(domain):
    _defaults = {
        **get_accountdefaults(domain),
        **postmasterdefaults,
    }
    return _defaults
