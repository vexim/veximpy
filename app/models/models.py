# coding: utf-8

#import string 
#from sqlalchemy import Column, Enum, ForeignKey, Index, Integer, SmallInteger, String, Table, Text
#from sqlalchemy.schema import FetchedValue
#from sqlalchemy.orm import relationship
#from flask import abort
#from flask_sqlalchemy import SQLAlchemy
from app.app import db, login_manager
#from instance.config import VEXIMDB_SCHEMA
from ..config.settings import groupdefaults, domaindefaults,  accountdefaults, settings
from flask_login import UserMixin
from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha256, pbkdf2_sha512
#from functools import wraps


class Blocklist(db.Model):
    __tablename__ = 'blocklists'
    __table_args__ = {'mysql_row_format': 'DYNAMIC'}

    block_id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.ForeignKey('domains.domain_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.ForeignKey('users.user_id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    blockhdr = db.Column(db.String(255, 'utf8mb4_unicode_ci'), nullable=False, server_default=db.FetchedValue())
    blockval = db.Column(db.String(255, 'utf8mb4_unicode_ci'), nullable=False, server_default=db.FetchedValue())
    color = db.Column(db.String(8, 'utf8mb4_unicode_ci'), nullable=False, server_default=db.FetchedValue())

    domain = db.relationship('Domain', primaryjoin='Blocklist.domain_id == Domain.domain_id', cascade="save-update, merge, delete", backref='blocklists_domain')
    user = db.relationship('User', primaryjoin='Blocklist.user_id == User.user_id', cascade="save-update, merge, delete", backref='blocklists_user')


class Domainalia(db.Model):
    __tablename__ = 'domainalias'
    __table_args__ = {'mysql_row_format': 'DYNAMIC'}

    domainalias_id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.ForeignKey('domains.domain_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    alias = db.Column(db.String(255, 'utf8mb4_unicode_ci'), nullable=False, unique=True, index=True)
    enabled = db.Column(db.Integer, nullable=False, server_default=str(domaindefaults['enabled']))
    host_smtp = db.Column(db.String(64, 'utf8mb4_unicode_ci'), server_default=domaindefaults['host_smtp'])
    host_imap = db.Column(db.String(64, 'utf8mb4_unicode_ci'), server_default=domaindefaults['host_imap'])
    host_pop = db.Column(db.String(64, 'utf8mb4_unicode_ci'), server_default=domaindefaults['host_pop'])

    domain = db.relationship('Domain', primaryjoin='Domainalia.domain_id == Domain.domain_id', backref='domainalias')

    @property
    def id(self):
        return(self.domainalias_id)

    @property
    def domainname(self):
        return(self.alias)

class Domain(db.Model):
    __tablename__ = 'domains'
    __table_args__ = {'mysql_row_format': 'DYNAMIC'}

    domain_id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255, 'utf8mb4_unicode_ci'), nullable=False, unique=True, server_default='', index=True)
    maildir = db.Column(db.String(4096, 'utf8mb4_unicode_ci'), nullable=False, server_default=domaindefaults['maildir'])
    uid = db.Column(db.SmallInteger, nullable=False, server_default=str(domaindefaults['uid']))
    gid = db.Column(db.SmallInteger, nullable=False, server_default=str(domaindefaults['gid']))
    max_accounts = db.Column(db.Integer, nullable=False, server_default=str(domaindefaults['max_accounts']))
    quotas = db.Column(db.Integer, nullable=False, server_default=str(domaindefaults['quotas']))
    quotasmax = db.Column(db.Integer, nullable=False, server_default=str(domaindefaults['quotasmax']))
    type = db.Column(db.String(5, 'utf8mb4_unicode_ci'))
    avscan = db.Column(db.Integer, nullable=False, server_default=str(domaindefaults['avscan']))
    blocklists = db.Column(db.Integer, nullable=False, server_default=str(domaindefaults['blocklists']))
    enabled = db.Column(db.Integer, nullable=False, server_default=str(domaindefaults['enabled']))
    mailinglists = db.Column(db.Integer, nullable=False, server_default=str(domaindefaults['mailinglists']))
    maxmsgsize = db.Column(db.Integer, nullable=False, server_default=str(domaindefaults['maxmsgsize']))
    pipe = db.Column(db.Integer, nullable=False, server_default=str(domaindefaults['pipe']))
    spamassassin = db.Column(db.Integer, nullable=False, server_default=str(domaindefaults['spamassassin']))
    sa_tag = db.Column(db.SmallInteger, nullable=False, server_default=str(domaindefaults['sa_tag']))
    sa_refuse = db.Column(db.SmallInteger, nullable=False, server_default=str(domaindefaults['sa_refuse']))
    out_ip = db.Column(db.String(255, 'utf8mb4_unicode_ci'), nullable=False, server_default=domaindefaults['out_ip'])
    host_smtp = db.Column(db.String(64, 'utf8mb4_unicode_ci'), server_default=domaindefaults['host_smtp'])
    host_imap = db.Column(db.String(64, 'utf8mb4_unicode_ci'), server_default=domaindefaults['host_imap'])
    host_pop = db.Column(db.String(64, 'utf8mb4_unicode_ci'), server_default=domaindefaults['host_pop'])
    relayto = db.Column(db.String(64, 'utf8mb4_unicode_ci'), server_default=domaindefaults['relayto'])
    pwd_charallowed = db.Column(db.String(255, 'utf8mb4_unicode_ci'), nullable=False, server_default=domaindefaults['pwd_charallowed'])
    pwd_lengthmin = db.Column(db.Integer, nullable=False, server_default=str(domaindefaults['pwd_lengthmin']))
    pwd_rules = db.Column(db.Integer, nullable=False, server_default=str(domaindefaults['pwd_rules']))

    PWDRULES_LOWER      = 0b00000001
    PWDRULES_UPPER      = 0b00000010
    PWDRULES_DIGIT      = 0b00000100
    PWDRULES_NONALPHA   = 0b00001000
    

    users = db.relationship('User', primaryjoin='User.domain_id == Domain.domain_id', cascade="save-update, merge, delete", backref='domains1', lazy='dynamic')
    localusers = db.relationship('User', primaryjoin='and_(User.domain_id == Domain.domain_id, User.type == "local")', cascade="save-update, merge, delete", backref='domains2', lazy='dynamic')
    aliasusers = db.relationship('User', primaryjoin='and_(User.domain_id == Domain.domain_id, User.type == "alias")', cascade="save-update, merge, delete", backref='domains3', lazy='dynamic')
    postmasters = db.relationship('User', primaryjoin='and_(User.domain_id == Domain.domain_id, User.role.op("&")(128) == 128)', backref='domains4', lazy='dynamic')
    aliases = db.relationship('Domainalia', primaryjoin='Domainalia.domain_id == Domain.domain_id', cascade="save-update, merge, delete", backref='domains5', lazy='dynamic')

    @property
    def id(self):
        return(self.domain_id)

    @property
    def domainname(self):
        return(self.domain)

    @property
    def is_deleteable(self):
        if self.enabled == 0 and self.id>1:
            if not self.type == 'local':
                print('local')
                return True
            if  self.aliases.count() == 0 and self.postmasters.count() == self.users.count():
                return True
        return False

    def __repr__(self):
        return '{}'.format(self.domain)

t_group_contents = db.Table(
    'group_contents',
    db.Column('group_id', db.ForeignKey('groups.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False, index=True),
    db.Column('member_id', db.ForeignKey('users.user_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False, index=True),
    #schema=VEXIMDB_SCHEMA
)


class Group(db.Model):
    __tablename__ = 'groups'
    __table_args__ = (
        db.Index('group_name', 'domain_id', 'name'),
        {'mysql_row_format': 'DYNAMIC'}
    )

    id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.ForeignKey('domains.domain_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(64, 'utf8mb4_unicode_ci'), nullable=False)
    is_public = db.Column(db.Integer, nullable=False, server_default=str(groupdefaults['is_public']))
    enabled = db.Column(db.Integer, nullable=False, server_default=str(groupdefaults['enabled']))

    domain = db.relationship('Domain', primaryjoin='Group.domain_id == Domain.domain_id', cascade="save-update, merge, delete", backref='groups')
    members = db.relationship('User', secondary='group_contents', backref='groups')


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = (
        db.Index('username', 'localpart', 'domain_id'),
        {'mysql_row_format': 'DYNAMIC'}
    )

    user_id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.ForeignKey('domains.domain_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    localpart = db.Column(db.String(255, 'utf8mb4_unicode_ci'), nullable=False, index=True, server_default='')
    username = db.Column(db.String(255, 'utf8mb4_unicode_ci'), nullable=False, server_default='')
    clear = db.Column(db.String(255, 'utf8mb4_unicode_ci'))
    crypt = db.Column(db.String(255, 'utf8mb4_unicode_ci'))
    uid = db.Column(db.SmallInteger, nullable=False, server_default=str(domaindefaults['uid']))
    gid = db.Column(db.SmallInteger, nullable=False, server_default=str(domaindefaults['gid']))
    smtp = db.Column(db.String(4096, 'utf8mb4_unicode_ci'), server_default='')
    pop = db.Column(db.String(4096, 'utf8mb4_unicode_ci'), server_default='')
    type = db.Column(db.Enum('local', 'alias', 'catch', 'fail', 'piped', 'admin', 'site'), nullable=False, server_default='local')
    admin = db.Column(db.Integer, nullable=False, server_default='0')
    on_avscan = db.Column(db.Integer, nullable=False, server_default=str(domaindefaults['avscan']))
    on_blocklist = db.Column(db.Integer, nullable=False, server_default=str(domaindefaults['blocklists']))
    on_forward = db.Column(db.Integer, nullable=False, server_default='0')
    on_piped = db.Column(db.Integer, nullable=False, server_default='0')
    on_spamassassin = db.Column(db.Integer, nullable=False, server_default='1')
    on_vacation = db.Column(db.Integer, nullable=False, server_default='0')
    spam_drop = db.Column(db.Integer, nullable=False, server_default='0')
    enabled = db.Column(db.Integer, nullable=False, server_default=str(domaindefaults['enabled']))
    flags = db.Column(db.String(16, 'utf8mb4_unicode_ci'))
    forward = db.Column(db.String(4096, 'utf8mb4_unicode_ci'), server_default='')
    unseen = db.Column(db.Integer, nullable=False, server_default='0')
    maxmsgsize = db.Column(db.Integer, nullable=False, server_default=str(domaindefaults['maxmsgsize']))
    quota = db.Column(db.Integer, nullable=False, server_default=str(accountdefaults['quota']))
    realname = db.Column(db.String(255, 'utf8mb4_unicode_ci'))
    sa_tag = db.Column(db.SmallInteger, nullable=False, server_default=str(domaindefaults['sa_tag']))
    sa_refuse = db.Column(db.SmallInteger, nullable=False, server_default=str(domaindefaults['sa_refuse']))
    tagline = db.Column(db.String(255, 'utf8mb4_unicode_ci'))
    vacation = db.Column(db.Text(collation='utf8mb4_unicode_ci'))
    comment = db.Column(db.String(255, 'utf8mb4_unicode_ci'))
    role = db.Column(db.Integer, nullable=False, server_default='0')

    domains = db.relationship('Domain', primaryjoin='User.domain_id == Domain.domain_id', backref='users1', lazy='joined')

    @property
    def id(self):
        return(self.user_id)

    @property
    def domainname(self):
        return(self.domains.domain)

    @property
    def is_active(self):
        return(self.enabled == 1)

    @property
    def is_piped(self):
        return(self.smtp[:1] == '|')

    @property
    def is_siteadmin(self):
        return(self.role & settings['ROLE_SITEADMIN'] == settings['ROLE_SITEADMIN'])

    # returns the domain_id if its a postmaster otherwise 0
    @property
    def is_postmaster(self):
        if self.role & settings['ROLE_POSTMASTER'] == settings['ROLE_POSTMASTER']:
            return self.domain_id
        return 0

    @property
    def is_deleteable(self):
        if self.is_siteadmin:
            return False
        if self.enabled == 0 and self.id>1:
            if self.is_postmaster == 0 or settings['POSTMASTER_DELETEALLOW'] == 1:
                return True
        return False

#    @property
#    def password(self):
#        """
#        Prevent password from being accessed
#        """
#        raise AttributeError('password is not a readable attribute.')

    @property
    def clear(self):
        """
        Prevent password from being accessed
        """
        raise AttributeError('password is not a readable attribute.')
    
#    @property
#    def crypt(self):
#        """
#        Prevent password from being accessed
#        """
#        raise AttributeError('password is not a readable attribute.')

#    @crypt.setter
    def password_set(self, password):
        """
        Set password to a hashed password
        """
        if settings['PWD_CRYPT_METHOD'] == 'pbkdf2_sha256':
            self.crypt = pbkdf2_sha256.hash(password)
        else:
            self.crypt = pbkdf2_sha512.hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        crypt_context = CryptContext(schemes=['md5_crypt', 'pbkdf2_sha256', 'pbkdf2_sha512'])
        return crypt_context.verify(password, self.crypt)

    @property
    def has_password(self):
        return (self.crypt is not None) and self.crypt != '' and self.crypt[0] != '!'

    def __repr__(self):
        return '{}'.format(self.username)

# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
