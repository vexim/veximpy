# app/config/config.py

import string

# Some extra characters to be added to the allowed chars for passwords
# In password rules these characters are treated like special (not isalpha) characters
pwdcharslig = 'öäüÖÄÜß'

settings = {
    'USERNAMES_SITEWIDE': 0,            # allow sitewide unique usernames (without domainpart)
    'CHECK_RCPT_REMOTE_LOCALPARTS': '', # a regex for matching usernames/mailaddresses. see exim4 CHECK_RCPT_REMOTE_LOCALPARTS
    # right now the RFC is stupid - https://tools.ietf.org/html/rfc6530#section-7.1 - it allowes a lot more characters
    # this is default but add what you think your yousers need. eg: !#$%&'*+-/=?^_`{|}~;
    # eMail addresses are _not_ case sensitive. even some $$$-companies believe the oposite.
    'USERNAMES_CHARSALLOWED': string.ascii_lowercase + string.digits + "!#$%&*+-/=?^_{|}~.",

    # default settings for passwords
    # PWDLENGTHMIN is a default _and_ a minimum value
    'PWDLENGTHMIN': 10,
    'PWDCHARSLIG': pwdcharslig, 
    'PWDCHARSALLOWED': string.ascii_letters + string.digits + '!§%&/()=?,.-;:_ <>|\{[]}@#+*~^°' + pwdcharslig,
    
    # defaults for domains
    # some of these settings in the domain table are defaults or min/max values for user account creation
    'DOMAINDEFAULT_MAILDIR': '/var/vmail', # path for maildirs. domainname will be appended to this
    'DOMAINDEFAULT_UID': 99,            # system uid
    'DOMAINDEFAULT_GID': 99,            # system gid
    'DOMAINDEFAULT_MAXACCOUNTS': 2147483647, # max. accounts; per domain
    'DOMAINDEFAULT_QUOTAS': 500,        # MB, default quota, 0 means unlimited; per user
    'DOMAINDEFAULT_QUOTASMAX': 1000,    # MB, max quota, 0 means unlimited; per user
    'DOMAINDEFAULT_AVSCAN': 1,          # antivirus; per user
    'DOMAINDEFAULT_BLOCKLISTS': 0,      # enable blocklists; per user
    'DOMAINDEFAULT_ENABLED': 1,         # enable domain
    'DOMAINDEFAULT_MAILINGLISTS': 0,    #
    'DOMAINDEFAULT_MAXMSGSIZE': 5000,   # kB, max. size per message; per user
    'DOMAINDEFAULT_PIPE': 0,            # allow pipe to command for users
    'DOMAINDEFAULT_SPAMASSASSIN': 1,    # enable spamassassin; per user
    'DOMAINDEFAULT_SA_TAG': 3,          # tag msg above this score; per user
    'DOMAINDEFAULT_SA_REFUSE': 5,       # reject msg above this score; per user
    'DOMAINDEFAULT_OUT_IP': '',         # semicolon seperated list of outgoing IPv4/6; per domain
                                        # OUT_IP is useful if you have one IP per domain
    'DOMAINDEFAULT_HOST_SMTP': 'mail1',
    'DOMAINDEFAULT_HOST_IMAP': 'mail1',
    'DOMAINDEFAULT_HOST_POP': 'mail1',
    'DOMAINDEFAULT_RELAYTO': '',        # relay messages to this server (IP)
    
    
    # some defaultvalues for postmaster accounts
    'POSTMASTER_DELETEALLOW': 0, 
    'POSTMASTER_CHANGEUIDGID': 0, 
    'POSTMASTERDEFAULT_QUOTA': 100,
    'POSTMASTERDEFAULT_MAXMSGSIZE': 5000,
    'POSTMASTERDEFAULT_ON_BLOCKLIST': 0, 
    'POSTMASTERDEFAULT_ON_AVSCAN': 0,
    'POSTMASTERDEFAULT_ON_SPAMASSASSIN': 1,
    'POSTMASTERDEFAULT_SA_TAG': 5,
    'POSTMASTERDEFAULT_SA_REFUSE': 10,
    'POSTMASTERDEFAULT_SPAM_DROP': 1,
    'POSTMASTERDEFAULT_ON_FORWARD': 0,
    'POSTMASTERDEFAULT_FORWARD': '',
    'POSTMASTERDEFAULT_UNSEEN': 0,
    'POSTMASTERDEFAULT_ON_VACATION': 0,
    'POSTMASTERDEFAULT_VACATION': '', 
    'POSTMASTERDEFAULT_ROLE': 0b10000000,
    
    # defaults for groups
    # https://github.com/vexim/vexim2/wiki/Group-Feature
    'GROUPDEFAULT_IS_PUBLIC': 0, 
    'GROUPDEFAULT_ENABLED': 1, 
}

"""
end of configuration
"""

# some checks for variables in settings
if (settings['DOMAINDEFAULT_QUOTAS'] > settings['DOMAINDEFAULT_QUOTASMAX'] or settings['DOMAINDEFAULT_QUOTAS'] == 0) and settings['DOMAINDEFAULT_QUOTASMAX'] > 0:
    raise ValueError('ValueError in settings.py. (DOMAINDEFAULT_QUOTAS > DOMAINDEFAULT_QUOTASMAX or (DOMAINDEFAULT_QUOTAS == 0) and DOMAINDEFAULT_QUOTASMAX > 0)')
