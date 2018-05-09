# coding: utf-8

#import string 
from sqlalchemy import Column, Enum, ForeignKey, Index, Integer, SmallInteger, String, Table, Text
from sqlalchemy.schema import FetchedValue
from sqlalchemy.orm import relationship
from flask import abort
from flask_sqlalchemy import SQLAlchemy
from app.app import db, login_manager
from .config.settings import settings
from flask_login import current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from passlib.context import CryptContext
from functools import wraps


class Blocklist(db.Model):
    __tablename__ = 'blocklists'
    __table_args__ = {'schema': 'veximtest', 'mysql_row_format': 'DYNAMIC'}

    block_id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.ForeignKey('veximtest.domains.domain_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.ForeignKey('veximtest.users.user_id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    blockhdr = db.Column(db.String(255, 'utf8mb4_unicode_ci'), nullable=False, server_default=db.FetchedValue())
    blockval = db.Column(db.String(255, 'utf8mb4_unicode_ci'), nullable=False, server_default=db.FetchedValue())
    color = db.Column(db.String(8, 'utf8mb4_unicode_ci'), nullable=False, server_default=db.FetchedValue())

    domain = db.relationship('Domain', primaryjoin='Blocklist.domain_id == Domain.domain_id', cascade="save-update, merge, delete", backref='blocklists_domain')
    user = db.relationship('User', primaryjoin='Blocklist.user_id == User.user_id', cascade="save-update, merge, delete", backref='blocklists_user')


class Domainalia(db.Model):
    __tablename__ = 'domainalias'
    __table_args__ = {'schema': 'veximtest', 'mysql_row_format': 'DYNAMIC'}

    domainalias_id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.ForeignKey('veximtest.domains.domain_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    alias = db.Column(db.String(255, 'utf8mb4_unicode_ci'), nullable=False, unique=True, index=True)
    enabled = db.Column(db.Integer, nullable=False, server_default=str(settings['DOMAINDEFAULT_ENABLED']))
    host_smtp = db.Column(db.String(64, 'utf8mb4_unicode_ci'), server_default=settings['DOMAINDEFAULT_HOST_SMTP'])
    host_imap = db.Column(db.String(64, 'utf8mb4_unicode_ci'), server_default=settings['DOMAINDEFAULT_HOST_IMAP'])
    host_pop = db.Column(db.String(64, 'utf8mb4_unicode_ci'), server_default=settings['DOMAINDEFAULT_HOST_POP'])

    domain = db.relationship('Domain', primaryjoin='Domainalia.domain_id == Domain.domain_id', backref='domainalias')

    @property
    def id(self):
        return(self.domainalias_id)

    @property
    def domainname(self):
        return(self.alias)

class Domain(db.Model):
    __tablename__ = 'domains'
    __table_args__ = {'schema': 'veximtest', 'mysql_row_format': 'DYNAMIC'}

    domain_id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255, 'utf8mb4_unicode_ci'), nullable=False, unique=True, server_default='', index=True)
    maildir = db.Column(db.String(4096, 'utf8mb4_unicode_ci'), nullable=False, server_default=settings['DOMAINDEFAULT_MAILDIR'])
    uid = db.Column(db.SmallInteger, nullable=False, server_default=str(settings['DOMAINDEFAULT_UID']))
    gid = db.Column(db.SmallInteger, nullable=False, server_default=str(settings['DOMAINDEFAULT_GID']))
    max_accounts = db.Column(db.Integer, nullable=False, server_default=str(settings['DOMAINDEFAULT_MAXACCOUNTS']))
    quotas = db.Column(db.Integer, nullable=False, server_default=str(settings['DOMAINDEFAULT_QUOTAS']))
    quotasmax = db.Column(db.Integer, nullable=False, server_default=str(settings['DOMAINDEFAULT_QUOTASMAX']))
    type = db.Column(db.String(5, 'utf8mb4_unicode_ci'))
    avscan = db.Column(db.Integer, nullable=False, server_default=str(settings['DOMAINDEFAULT_AVSCAN']))
    blocklists = db.Column(db.Integer, nullable=False, server_default=str(settings['DOMAINDEFAULT_BLOCKLISTS']))
    enabled = db.Column(db.Integer, nullable=False, server_default=str(settings['DOMAINDEFAULT_ENABLED']))
    mailinglists = db.Column(db.Integer, nullable=False, server_default=str(settings['DOMAINDEFAULT_MAILINGLISTS']))
    maxmsgsize = db.Column(db.Integer, nullable=False, server_default=str(settings['DOMAINDEFAULT_MAXMSGSIZE']))
    pipe = db.Column(db.Integer, nullable=False, server_default=str(settings['DOMAINDEFAULT_PIPE']))
    spamassassin = db.Column(db.Integer, nullable=False, server_default=str(settings['DOMAINDEFAULT_SPAMASSASSIN']))
    sa_tag = db.Column(db.SmallInteger, nullable=False, server_default=str(settings['DOMAINDEFAULT_SA_TAG']))
    sa_refuse = db.Column(db.SmallInteger, nullable=False, server_default=str(settings['DOMAINDEFAULT_SA_REFUSE']))
    out_ip = db.Column(db.String(255, 'utf8mb4_unicode_ci'), nullable=False, server_default=settings['DOMAINDEFAULT_OUT_IP'])
    host_smtp = db.Column(db.String(64, 'utf8mb4_unicode_ci'), server_default=settings['DOMAINDEFAULT_HOST_SMTP'])
    host_imap = db.Column(db.String(64, 'utf8mb4_unicode_ci'), server_default=settings['DOMAINDEFAULT_HOST_IMAP'])
    host_pop = db.Column(db.String(64, 'utf8mb4_unicode_ci'), server_default=settings['DOMAINDEFAULT_HOST_POP'])
    relayto = db.Column(db.String(64, 'utf8mb4_unicode_ci'), server_default=settings['DOMAINDEFAULT_RELAYTO'])
    pwd_charallowed = db.Column(db.String(255, 'utf8mb4_unicode_ci'), nullable=False, server_default=settings['PWDCHARSALLOWED'])
    pwd_lengthmin = db.Column(db.Integer, nullable=False, server_default=str(settings['PWDLENGTHMIN']))
    pwd_rules = db.Column(db.Integer, nullable=False, server_default='255')

    PWDRULES_LOWER      = 0b00000001
    PWDRULES_UPPER      = 0b00000010
    PWDRULES_DIGIT      = 0b00000100
    PWDRULES_NONALPHA   = 0b00001000
    

    users = db.relationship('User', primaryjoin='User.domain_id == Domain.domain_id', cascade="save-update, merge, delete", backref='domains1', lazy='dynamic')
    localusers = db.relationship('User', primaryjoin='and_(User.domain_id == Domain.domain_id, User.type == "local")', cascade="save-update, merge, delete", backref='domains2', lazy='dynamic')
    aliasusers = db.relationship('User', primaryjoin='and_(User.domain_id == Domain.domain_id, User.type == "alias")', cascade="save-update, merge, delete", backref='domains3', lazy='dynamic')
    postmasters = db.relationship('User', primaryjoin='and_(User.domain_id == Domain.domain_id, User.role.op("&")(8) == 8)', backref='domains4', lazy='dynamic')
    aliases = db.relationship('Domainalia', primaryjoin='Domainalia.domain_id == Domain.domain_id', cascade="save-update, merge, delete", backref='domains5', lazy='dynamic')

    @property
    def id(self):
        return(self.domain_id)

    @property
    def domainname(self):
        return(self.domain)

    def __repr__(self):
        return '{}'.format(self.domain)

t_group_contents = db.Table(
    'group_contents',
    db.Column('group_id', db.ForeignKey('veximtest.groups.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False, index=True),
    db.Column('member_id', db.ForeignKey('veximtest.users.user_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False, index=True),
    schema='veximtest'
)


class Group(db.Model):
    __tablename__ = 'groups'
    __table_args__ = (
        db.Index('group_name', 'domain_id', 'name'),
        {'schema': 'veximtest', 'mysql_row_format': 'DYNAMIC'}
    )

    id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.ForeignKey('veximtest.domains.domain_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(64, 'utf8mb4_unicode_ci'), nullable=False)
    is_public = db.Column(db.Integer, nullable=False, server_default=str(settings['GROUPDEFAULT_IS_PUBLIC']))
    enabled = db.Column(db.Integer, nullable=False, server_default=str(settings['GROUPDEFAULT_ENABLED']))

    domain = db.relationship('Domain', primaryjoin='Group.domain_id == Domain.domain_id', cascade="save-update, merge, delete", backref='groups')
    members = db.relationship('User', secondary='veximtest.group_contents', backref='groups')


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = (
        db.Index('username', 'localpart', 'domain_id'),
        {'schema': 'veximtest', 'mysql_row_format': 'DYNAMIC'}
    )

    user_id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.ForeignKey('veximtest.domains.domain_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    localpart = db.Column(db.String(255, 'utf8mb4_unicode_ci'), nullable=False, index=True, server_default='')
    username = db.Column(db.String(255, 'utf8mb4_unicode_ci'), nullable=False, server_default='')
    clear = db.Column(db.String(255, 'utf8mb4_unicode_ci'))
    crypt = db.Column(db.String(255, 'utf8mb4_unicode_ci'))
    uid = db.Column(db.SmallInteger, nullable=False, server_default=str(settings['DOMAINDEFAULT_UID']))
    gid = db.Column(db.SmallInteger, nullable=False, server_default=str(settings['DOMAINDEFAULT_GID']))
    smtp = db.Column(db.String(4096, 'utf8mb4_unicode_ci'), server_default='')
    pop = db.Column(db.String(4096, 'utf8mb4_unicode_ci'), server_default='')
    type = db.Column(db.Enum('local', 'alias', 'catch', 'fail', 'piped', 'admin', 'site'), nullable=False, server_default='local')
    admin = db.Column(db.Integer, nullable=False, server_default='0')
    on_avscan = db.Column(db.Integer, nullable=False, server_default=str(settings['DOMAINDEFAULT_AVSCAN']))
    on_blocklist = db.Column(db.Integer, nullable=False, server_default=str(settings['DOMAINDEFAULT_BLOCKLISTS']))
    on_forward = db.Column(db.Integer, nullable=False, server_default='0')
    on_piped = db.Column(db.Integer, nullable=False, server_default='0')
    on_spamassassin = db.Column(db.Integer, nullable=False, server_default='1')
    on_vacation = db.Column(db.Integer, nullable=False, server_default='0')
    spam_drop = db.Column(db.Integer, nullable=False, server_default='0')
    enabled = db.Column(db.Integer, nullable=False, server_default=str(settings['DOMAINDEFAULT_ENABLED']))
    flags = db.Column(db.String(16, 'utf8mb4_unicode_ci'))
    forward = db.Column(db.String(4096, 'utf8mb4_unicode_ci'), server_default='')
    unseen = db.Column(db.Integer, nullable=False, server_default='0')
    maxmsgsize = db.Column(db.Integer, nullable=False, server_default=str(settings['DOMAINDEFAULT_MAXMSGSIZE']))
    quota = db.Column(db.Integer, nullable=False, server_default=str(settings['DOMAINDEFAULT_QUOTAS']))
    realname = db.Column(db.String(255, 'utf8mb4_unicode_ci'))
    sa_tag = db.Column(db.SmallInteger, nullable=False, server_default=str(settings['DOMAINDEFAULT_SA_TAG']))
    sa_refuse = db.Column(db.SmallInteger, nullable=False, server_default=str(settings['DOMAINDEFAULT_SA_REFUSE']))
    tagline = db.Column(db.String(255, 'utf8mb4_unicode_ci'))
    vacation = db.Column(db.Text(collation='utf8mb4_unicode_ci'))
    comment = db.Column(db.String(255, 'utf8mb4_unicode_ci'))
    role = db.Column(db.Integer, nullable=False, server_default='0')

    domains = db.relationship('Domain', primaryjoin='User.domain_id == Domain.domain_id', backref='users1')

    ROLE_SITEADMIN      = 0b10000000 # int 128
    ROLE_POSTMASTER     = 0b00001000 # int 8
    
    @property
    def id(self):
        return(self.user_id)

    @property
    def is_active(self):
        return(self.enabled == 1)

    @property
    def is_piped(self):
        return(self.smtp[:1] == '|')

    @property
    def is_siteadmin(self):
        return(self.role & self.ROLE_SITEADMIN)

    @property
    def is_postmaster(self):
        if self.domains.enabled and (self.role & self.ROLE_POSTMASTER):
            return self.domain_id
        return 0

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
        self.crypt = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        # return check_password_hash(self.crypt, password)
        crypt_context = CryptContext(schemes=['md5_crypt', 'pbkdf2_sha256'])
        #return crypt_context.hash(password)
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

