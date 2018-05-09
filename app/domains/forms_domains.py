# app/domains/forms_domains.py

from os import path
from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, PasswordField, SelectField, StringField, SubmitField
from wtforms_components import read_only
from ..lib.forms_functions import TextAreaSepListField, IPList, PasswordRules, URI, DomainExists, bool_checked
from wtforms.validators import DataRequired, EqualTo, IPAddress, Length, NumberRange, Optional
from ..config.settings import settings

class DomainFormLocal(FlaskForm):
    """
    Form for add/edit domains
    """

    def __init__(self, obj=None, action='add', *args, **kwargs):
        super().__init__(obj=obj)
        self.action = action.lower()
        #self.process(obj=obj)
        if action.lower() == 'add':
            del self.submitedit
        elif action.lower() == 'edit':
            del self.password1
            del self.password2
            del self.submitadd
            read_only(self.domain)
            self.domain.validators = []
            read_only(self.maildir)
            self.maildir.description = ''
            self.maildir.validators = []
            #form.password1.flags.required = False
            self.pwdcharallowed = self.pwd_charallowed.data

    def domain_save(self, domain):
        if self.action == 'add':
            self.password1.flags.required = True
        if self.validate_on_submit():
            is_mailinglist = 0
            self.populate_obj(domain)
            domain.maildir = path.join(self.maildir.data, self.domain.data)
            domain.blocklists = 0
            domain.mailinglists = is_mailinglist
            domain.type = 'local'
            return True
        return False

#    def validate(self):
#        print(self.submitadd.__dict__)
#        print(self.submitcancel.__dict__)
#        if self.submitcancel.data and not FlaskForm.validate(self):
#            return False
#        return True

    action = 'add'
    pwdcharallowed = settings['PWDCHARSALLOWED']
    pwdlengthmin = settings['PWDLENGTHMIN']

    enabled = BooleanField('Enabled', default=bool_checked(settings['DOMAINDEFAULT_ENABLED']), false_values={0, False, 'false', ''})
    domain = StringField('Domain', validators=[Length(min=3, max=255), URI, DomainExists])
    maildir = StringField('Maildir base path. Domain name will be appended.', description='You can <b>not</b> change this later.', default='/var/vmail/', validators=[Length(min=3, max=4096)])
    password1 = PasswordField('Password for postmaster account', validators=[PasswordRules, EqualTo('password2', message='Password does not match confirmation password.')])
    password2 = PasswordField('Confirm Password')
    uid = IntegerField('System UID', default=settings['DOMAINDEFAULT_UID'], validators=[NumberRange(min=99, max=65535)])
    gid = IntegerField('System GID', default=settings['DOMAINDEFAULT_GID'], validators=[NumberRange(min=99, max=65535)])
    max_accounts = IntegerField('Max. Accounts', default=settings['DOMAINDEFAULT_MAXACCOUNTS'], validators=[NumberRange(min=1, max=2147483647)])
    quotas = IntegerField('Quota for each account [MB]. 0 means unlimited', default=settings['DOMAINDEFAULT_QUOTAS'], validators=[NumberRange(min=0, max=2147483647)])
    quotasmax = IntegerField('Quota for each account [MB]. 0 means unlimited', default=settings['DOMAINDEFAULT_QUOTASMAX'], validators=[NumberRange(min=0, max=2147483647)])
    maxmsgsize = IntegerField('Max. message size [kB]', description='The maximum size for incoming mail (user tunable)', default=5000, validators=[NumberRange(min=1000, max=2147483647)])
    #type = StringField('Domain type', default = 'local', validators=[DataRequired(), Length(min=1, max=5)])
    avscan = BooleanField('Anti virus scan', description='Run anti virus scan on mails.', default=bool_checked(settings['DOMAINDEFAULT_AVSCAN']), false_values={0, False, 'false', ''})
    spamassassin = BooleanField('Spam check', description='Run spamassassin on mails.', default=bool_checked(settings['DOMAINDEFAULT_SPAMASSASSIN']), false_values={0, False, 'false', ''})
    sa_tag = IntegerField('Tag spam above this score', description='Above this score the "X-Spam-Flag: YES" header will be added.', default=settings['DOMAINDEFAULT_SA_TAG'], validators=[NumberRange(min=0, max=99)])
    sa_refuse = IntegerField('Refuse spam above this score', default=settings['DOMAINDEFAULT_SA_REFUSE'], validators=[NumberRange(min=0, max=99)])
    #blocklists = 
    #mailinglists = 
    pipe = BooleanField('Allow piping mails to programs', default=bool_checked(settings['DOMAINDEFAULT_PIPE']), false_values={0, False, 'false', ''})
    out_ip = TextAreaSepListField('Outgoing IPs. List of IPv4/IPv6 addresses. One per line.', default=settings['DOMAINDEFAULT_OUT_IP'], validators=[Length(min=0, max=255), IPList], separator=' ; ', render_kw={"rows": 5, "cols": 255})
    host_smtp = StringField('SMTP host', default=settings['DOMAINDEFAULT_HOST_SMTP'], validators=[DataRequired(), Length(min=2, max=64)])
    host_imap = StringField('IMAP host', default=settings['DOMAINDEFAULT_HOST_IMAP'], validators=[DataRequired(), Length(min=2, max=64)])
    host_pop = StringField('POP3 host', default=settings['DOMAINDEFAULT_HOST_POP'], validators=[DataRequired(), Length(min=2, max=64)])
    relayto = StringField('Relay mails to IP', default=settings['DOMAINDEFAULT_RELAYTO'], validators=[Optional(), IPAddress(ipv4=True, ipv6=True)])
    pwd_charallowed = StringField('Allowed password characters', default=settings['PWDCHARSALLOWED'], validators=[Length(min=64, max=255)])
    pwd_lengthmin = IntegerField('Minimum length for passwords', default=settings['PWDLENGTHMIN'], validators=[NumberRange(min=settings['PWDLENGTHMIN'], max=2147483647)])
    #pwd_rules
    submitadd = SubmitField('Add domain')
    submitedit = SubmitField('Save domain')
    submitcancel = SubmitField('Cancel')

class DomainFormAlias(FlaskForm):

    def __init__(self, obj=None, action='add',  **kwargs):
        super().__init__(obj=obj)
        if action.lower() == 'add':
            del self.submitedit
        elif action.lower() == 'edit':
            del self.submitadd
            read_only(self.alias)
            self.alias.validators = []

    def domain_save(self, domain):
        if self.validate_on_submit():
            is_mailinglist = 0
            self.populate_obj(domain)
            domain.blocklists = 0
            domain.mailinglists = is_mailinglist
            domain.type = 'alias'
            return True
        return False

    enabled = BooleanField('Enabled', default=bool_checked(settings['DOMAINDEFAULT_ENABLED']), false_values={0, False, 'false', ''})
    alias = StringField('Domain', validators=[Length(min=3, max=255), URI, DomainExists])
    domain_id = SelectField('Redirect mails to', coerce=int)
    host_smtp = StringField('SMTP host', default='mail', validators=[DataRequired(), Length(min=2, max=64)])
    host_imap = StringField('IMAP host', default='mail', validators=[DataRequired(), Length(min=2, max=64)])
    host_pop = StringField('POP3 host', default='mail', validators=[DataRequired(), Length(min=2, max=64)])
    submitadd = SubmitField('Add domain')
    submitedit = SubmitField('Save domain')
    submitcancel = SubmitField('Cancel')
   
class DomainFormRelay(FlaskForm):

    def __init__(self, obj=None, action='add',  **kwargs):
        super().__init__(obj=obj)
        if action.lower() == 'add':
            del self.submitedit
        elif action.lower() == 'edit':
            del self.submitadd
            read_only(self.domain)
            self.domain.validators = []

    def domain_save(self, domain):
        if self.validate_on_submit():
            is_mailinglist = 0
            self.populate_obj(domain)
            domain.blocklists = 0
            domain.mailinglists = is_mailinglist
            domain.type = 'relay'
            return True
        return False

    enabled = BooleanField('Enabled', default=bool_checked(settings['DOMAINDEFAULT_ENABLED']), false_values={0, False, 'false', ''})
    domain = StringField('Domain', validators=[Length(min=3, max=255), URI, DomainExists])
    submitadd = SubmitField('Add domain')
    submitedit = SubmitField('Save domain')
    submitcancel = SubmitField('Cancel')

class DomainFormMailinglist(FlaskForm):
    pass
