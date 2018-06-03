# app/config/settings.py

import string

# Some extra characters to be added to the allowed chars for passwords
# In password rules these characters are treated like special (not isalpha) characters
pwdchars_lig = 'öäüÖÄÜß'

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
    'PWDCHARSLIG': pwdchars_lig,
    'PWDCHARSALLOWED': string.ascii_letters + string.digits + '!§%&/()=?,.-;:_ <>|\{[]}@#+*~^°' + pwdchars_lig,
    'PWD_CRYPT_METHOD': 'pbkdf2_sha512',    # algorythmus for password hashing (module passlib.hash)

    # some defaultvalues for postmaster accounts
    'POSTMASTER_DELETEALLOW': 0,    # allow deletion of postmaster accounts
    'POSTMASTER_CHANGEUIDGID': 0,   # 
    
    'ROLE_SITEADMIN':   0b1000000000000000,   # int 32896
    'ROLE_POSTMASTER':          0b10000000,   # int 128'
    'ROLE_USER':                0b00000000,   # int 0'
}

"""
defaults for groups
https://github.com/vexim/vexim2/wiki/Group-Feature
"""
groupdefaults = {

    'is_public': 0,
    'enabled': 1,
}

"""
defaults for domains table
some of these settings in the domain table are defaults or min/max values for user account creation
the keys of this dictionary correspond to the fields in the DB
"""
domaindefaults = {
    'maildir': '/var/vmail',    # path for maildirs. domainname will be appended to this
    'uid': 99,                  # system uid
    'gid': 99,                  # system gid
    'max_accounts': 2147483647, # max. accounts; per domain
    'quotas': 500,              # MB, default quota, 0 means unlimited; per user
    'quotasmax': 1000,          # MB, max quota, 0 means unlimited; per user
    'type': 'local',            # domain type
    'avscan': 1,                # antivirus; per user
    'blocklists': 0,            # enable blocklists; per user
    'enabled': 1,               # enable domain
    'mailinglists': 0,          #
    'maxmsgsize': 5000,         # kB, max. size per message; per user
    'pipe': 0,                  # allow pipe to command for users
    'spamassassin': 1,          # enable spamassassin; per user
    'sa_tag': 3,                # tag msg above this score; per user
    'sa_refuse': 5,             # reject msg above this score; per user
    'out_ip': '',               # semicolon seperated list of outgoing IPv4/6; per domain
                                # OUT_IP is useful if you have one IP per domain
    'host_smtp': 'mail1',
    'host_imap': 'mail1',
    'host_pop': 'mail1',
    'relayto': '',              # relay messages to this server (IP)
    'pwd_charallowed': settings['PWDCHARSALLOWED'],
    'pwd_lengthmin': settings['PWDLENGTHMIN'],
    'pwd_rules': '255',
}

aliasdomaindefaults = {
    'enabled': 1,               # enable domain
    'host_smtp': 'mail1',
    'host_imap': 'mail1',
    'host_pop': 'mail1',
}

sitedomaindefaults = {
    **domaindefaults,
    'domain_id': 1,
    'domain': "site",
}

accountdefaults = {
    'admin': 0,
    'quota': domaindefaults['quotas'],
    'on_blocklist': 0,          # enable blocklist
    'on_avscan': 1,             # enable antivirus scan
    'on_spamassassin': 1,       # enable spamassassin
    'spam_drop': 1,             # drop messages above sa_refuse score
    'on_forward': 0,            # enable forwarding of messages
    'forward': '',              # mailadresses to forward to
    'unseen': 0,                # disable local storage of forwarded messages
    'on_vacation': 0,           # enable vacation message
    'vacation': '',             # text for vacation message
    'role': settings['ROLE_USER'],
}

"""
some defaultvalues for postmaster accounts in users table
the keys of this dictionary correspond to the fields in the DB
"""
postmasterdefaults = {
    **accountdefaults,
    'admin': 1,
    'quota': 100,               # quota of the account
    'maxmsgsize': 5000,         # max. message size per message
    'on_blocklist': 0,          # enable blocklist
    'on_avscan': 0,             # enable antivirus scan
    'on_spamassassin': 1,       # enable spamassassin
    'sa_tag': 5,                # tag messages above this score
    'sa_refuse': 10,            # refuse messages above this score
    'spam_drop': 1,             # drop messages above sa_refuse score
    'forward': '',              # mailadresses to forward to
    'unseen': 0,                # disable local storage of forwarded messages
    'on_vacation': 0,           # enable vacation message
    'vacation': '',             # text for vacation message
    'role': settings['ROLE_POSTMASTER'], # set role to postmaster (128)
}

siteadmindefaults = {
    **accountdefaults,
    'user_id': 1,
    'domain_id': 1, 
    'localpart': "siteadmin", 
    'username': "siteadmin", 
    'admin': 1, 
    'role': settings['ROLE_SITEADMIN'], 
}

"""
end of configuration
"""

# some checks for variables in settings
if (domaindefaults['quotas'] > domaindefaults['quotasmax'] or domaindefaults['quotas'] == 0) and domaindefaults['quotasmax'] > 0:
    raise ValueError('ValueError in settings.py. (DOMAINDEFAULT_QUOTAS > DOMAINDEFAULT_QUOTASMAX or (DOMAINDEFAULT_QUOTAS == 0) and DOMAINDEFAULT_QUOTASMAX > 0)')
