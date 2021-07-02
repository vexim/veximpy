# app/accounts/forms.py
# This file is part of veximpy

from os import path
from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import EqualTo, Length, NumberRange, Optional
from wtforms_components import read_only
from ..lib.forms_fields import TextAreaSepListField
from ..lib.forms_functions import bool_checked
from ..lib.forms_validators import Localpart, Username, PasswordRules
from ..models.models import Domain #, User
from ..config.settings import domaindefaults, postmasterdefaults, settings


class AccountFormLocal(FlaskForm):
    """
    Form for add/edit accounts
    """

    action = 'add'
    domain = Domain()
    pwdcharallowed = settings['PWDCHARSALLOWED']
    pwdlengthmin = settings['PWDLENGTHMIN']
    role = settings['ROLE_USER']

    def __init__(self, label='', validators=None, obj=None, action='add', domain=None, *args, **kwargs):
        self.action = action.lower()
        if domain:
            self.domain = domain
        else:
            raise ValueError('No domain object in AccountFormLocal.__init__')

        super().__init__(obj=obj)
        self.pwdcharallowed = self.domain.pwd_charallowed
        self.pwdlengthmin = self.domain.pwd_lengthmin

        if self.domain.quotas == 0:
            _quotamin = 0
            _quotamax = 2147483647
        else:
            _quotamin = 10
            _quotamax = self.domain.quotas
        self.quota.validators=[NumberRange(min=_quotamin, max=_quotamax)]
        self.maxmsgsize.validators=[NumberRange(min=0, max=self.domain.maxmsgsize)]

        if self.action == 'add':
            del self.submitedit
            self.domain_id = self.domain.domain_id
        elif self.action == 'addpostmaster':
            del self.password2
            self.role = postmasterdefaults['role']
        elif self.action == 'edit':
            del self.submitadd
            self.password1.flags.required = False
            read_only(self.localpart)
            self.localpart.validators = []

        if settings['POSTMASTER_CHANGEUIDGID'] != 1:
            del self.uid
            del self.gid
        if self.localpart.data == 'postmaster':
            del self.username
            del self.enabled
            del self.admin
        if self.domain.pipe != 1:
            del self.on_pipe
            del self.smtp

    def account_save(self, account):
        if self.action in ['add', 'addpostmaster']:
            self.password1.flags.required = True
        if self.password1.data == '':
            del self.password1
            del self.password2

        if self.validate_on_submit():
            self.populate_obj(account)
            account.domain_id = self.domain.domain_id
            account.pop = path.join(self.domain.maildir, self.localpart.data)
            account.role = self.role
            account.type = 'local'

            if self.username and self.username.data == '':
                account.username = self.localpart.data + '@' + self.domain.domain
            if self.password1 and self.password1.data != '':
                account.password_set(self.password1.data)
            if settings['POSTMASTER_CHANGEUIDGID'] != 1:
                account.uid = self.domain.uid
                account.gid = self.domain.gid
            if self.localpart.object_data == 'postmaster':
                account.username = 'postmaster@' + self.domain.domain
                account.enabled = 1
                account.admin = 1
                account.role = account.role | settings['ROLE_POSTMASTER']
                print(account.role)
            if self.domain.pipe != 1:
                account.on_pipe = 0
                account.smtp = path.join(self.domain.maildir, self.localpart.data, 'Maildir')

            return True
        return False

    enabled = BooleanField('Enabled', false_values={0, False, 'false', ''})
    realname = StringField('Realname', description='', validators=[Length(min=1, max=255)])
    localpart = StringField('Localpart',
                    description='', validators=[Localpart, Length(min=1, max=255)])
    username = StringField('Username',
                    description='An arbitrary value. If empty the mailaddress of this account will be used.',
                    validators=[Username, Optional(), Length(min=0, max=255)])
    comment = StringField('Comment', validators=[Optional(), Length(min=0, max=255)])
    password1 = PasswordField('Password', validators=[PasswordRules])
    password2 = PasswordField('Confirm Password', validators=[EqualTo('password1',
                    message='Password does not match confirmation password.')])
    uid = IntegerField('System UID', validators=[NumberRange(min=99, max=65535)])
    gid = IntegerField('System GID', validators=[NumberRange(min=99, max=65535)])
    admin = BooleanField('Domain Admin', false_values={0, False, 'false', ''})
    on_pipe = BooleanField('Enable piping mails to programs',
                    false_values={0, False, 'false', ''})
    smtp = StringField('Pipe mails to this program or alternative Maildir (localpart/Maildir will be appended)',
                    description='For piping this should start with "|". Eg. "|/usr/bin/example_command.sh',
                    validators=[Length(min=1, max=4096)])
    #pop = StringField('Realname', validators=[Length(min=1, max=4096)])

    quota = IntegerField('Quota [MB]. 0 means unlimited')
    maxmsgsize = IntegerField('Max. message size [kB]',
                    description='The maximum size for incoming mail')
    #type = StringField('Domain type', default = 'local', validators=[DataRequired(), Length(min=1, max=5)])
    on_blocklist = BooleanField('Enable blocklist',
                    false_values={0, False, 'false', ''})
    on_avscan = BooleanField('Anti virus scan',
                    description='Run anti virus scan on mails.',
                    false_values={0, False, 'false', ''})
    on_spamassassin = BooleanField('Spam check',
                    description='Run spamassassin on mails.',
                    false_values={0, False, 'false', ''})
    sa_tag = IntegerField('Tag spam above this score',
                    description='Above this score the "X-Spam-Flag: YES" header will be added.',
                    validators=[NumberRange(min=0, max=99)])
    sa_refuse = IntegerField('Refuse spam above this score',
                    validators=[NumberRange(min=0, max=99)])
    spam_drop = BooleanField('Delete mails above "refuse score" if enabled. If disabled move them to the Junk folder.',
                    false_values={0, False, 'false', ''})
    on_forward = BooleanField('Enable mail forwarding',
                    false_values={0, False, 'false', ''})
    forward = TextAreaSepListField('Forward mails to following addresses. One per line.',
                    validators=[Length(min=0, max=4096)], separator=', ', render_kw={"rows": 5, "cols": 255})
    unseen = BooleanField('Store forwarded mail locally',
                    false_values={0, False, 'false', ''})
    on_vacation = BooleanField('Enable vacation message. Automatic reply.',
                    description='If possible use a sieve filter of your mail delivery agent. Ask your sysadmin.',
                    false_values={0, False, 'false', ''})
    vacation = TextAreaField('Vacation message', validators=[Length(min=0, max=255)])
    submitadd = SubmitField('Add accont')
    submitedit = SubmitField('Save account')
    submitcancel = SubmitField('Cancel', render_kw={'formnovalidate': True})


class AccountFormAlias(FlaskForm):
    """
    Form for add/edit alias accounts
    """

    action = 'add'
    domain = Domain()
    pwdcharallowed = settings['PWDCHARSALLOWED']
    pwdlengthmin = settings['PWDLENGTHMIN']

    def __init__(self, label='', validators=None, obj=None, action='add', domain=None, *args, **kwargs):
        self.action = action.lower()
        if domain:
            self.domain = domain
        else:
            raise ValueError('No domain object in AccountFormLocal.__init__')

        super().__init__(obj=obj)
        self.pwdcharallowed = self.domain.pwd_charallowed
        self.pwdlengthmin = self.domain.pwd_lengthmin

        if self.action == 'add':
            del self.submitedit
            self.domain_id = self.domain.domain_id
        elif self.action == 'addpostmaster':
            raise ValueError('Postmaster can not be an alias account')
        elif self.action == 'edit':
            del self.submitadd
            self.password1.flags.required = False
            read_only(self.localpart)
            self.localpart.validators = []

        if self.localpart.data == 'postmaster':
            raise ValueError('Postmaster can not be an alias account')

    def account_save(self, account):
        if self.password1.data == '':
            del self.password1
            del self.password2

        if self.validate_on_submit():
            self.populate_obj(account)
            account.domain_id = self.domain.domain_id
            account.pop = path.join(self.domain.maildir, self.localpart.data)
            account.role = settings['ROLE_USER']
            account.type = 'alias'

            if self.username and self.username.data == '':
                account.username = self.localpart.data + '@' + self.domain.domain
            if self.password1 and self.password1.data != '':
                account.password_set(self.password1.data)

            return True
        return False

    enabled = BooleanField('Enabled', default=bool_checked(domaindefaults['enabled']), false_values={0, False, 'false', ''})
    realname = StringField('Realname', validators=[Length(min=1, max=255)])
    localpart = StringField('Localpart', validators=[Length(min=1, max=255)])
    username = StringField('Username', validators=[Length(min=1, max=255)])
    comment = StringField('Comment', validators=[Optional(), Length(min=0, max=255)])
    password_remove = BooleanField('Remove Password. Deny Login.', default=bool_checked(), false_values={0, False, 'false', ''})
    password1 = PasswordField('Password', description='Password only needed if you want the user to be able to log in, or if the Alias is the admin account', validators=[PasswordRules, EqualTo('password2', message='Password does not match confirmation password.')])
    password2 = PasswordField('Confirm Password')
    admin = BooleanField('Domain Admin', default=0, false_values={0, False, 'false', ''})
    smtp = TextAreaSepListField('Address', description='Multiple addresses should be comma separated, with no spaces', validators=[Length(min=1, max=4096)], separator=', ', render_kw={"rows": 5, "cols": 255})
    on_avscan = BooleanField('Anti virus scan', description='Run anti virus scan on mails.', default=1, false_values={0, False, 'false', ''})
    on_spamassassin = BooleanField('Spam check', description='Run spamassassin on mails.', default=1, false_values={0, False, 'false', ''})
    sa_tag = IntegerField('Tag spam above this score', description='Above this score the "X-Spam-Flag: YES" header will be added.', default=3, validators=[NumberRange(min=0, max=99)])
    sa_refuse = IntegerField('Refuse spam above this score', default=5, validators=[NumberRange(min=0, max=99)])
    spam_drop = BooleanField('Move mails above "refuse score" to Junk folder or if disabled delete it.', default=1, false_values={0, False, 'false', ''})
    submitadd = SubmitField('Add account')
    submitedit = SubmitField('Save account')
    cancel = SubmitField('Cancel')


class AccountFormFail(FlaskForm):
    """
    Form for add/edit fail accounts
    """

    action = 'add'
    domain = Domain()
    pwdcharallowed = settings['PWDCHARSALLOWED']
    pwdlengthmin = settings['PWDLENGTHMIN']

    def __init__(self, label='', validators=None, obj=None, action='add', domain=None, *args, **kwargs):
        self.action = action.lower()
        if domain:
            self.domain = domain
        else:
            raise ValueError('No domain object in AccountFormLocal.__init__')

        super().__init__(obj=obj)

        if self.action == 'add':
            del self.submitedit
            self.domain_id = self.domain.domain_id
        elif self.action == 'addpostmaster':
            raise ValueError('Postmaster can not be a fail account')
        elif self.action == 'edit':
            del self.submitadd
            read_only(self.localpart)
            self.localpart.validators = []

        if self.localpart.data == 'postmaster':
            raise ValueError('Postmaster can not be an fail account')

    def account_save(self, account):

        if self.validate_on_submit():
            self.populate_obj(account)
            account.domain_id = self.domain.domain_id
            account.pop = path.join(self.domain.maildir, self.localpart.data)
            account.role = settings['ROLE_USER']
            account.type = 'fail'
            account.username = self.localpart.data + '@' + self.domain.domain

            return True
        return False

    enabled = BooleanField('Enabled', default=bool_checked(domaindefaults['enabled']), false_values={0, False, 'false', ''})
    localpart = StringField('Localpart', validators=[Length(min=1, max=255)])
    comment = StringField('Comment', validators=[Optional(), Length(min=0, max=255)])
    submitadd = SubmitField('Add account')
    submitedit = SubmitField('Save account')
    submitcancel = SubmitField('Cancel', render_kw={'formnovalidate': True})


class AccountFormMailinglist(FlaskForm):
    submitadd = SubmitField('Add account')
    submitedit = SubmitField('Save account')
    submitcancel = SubmitField('Cancel', render_kw={'formnovalidate': True})


class AccountFormCatchall(FlaskForm):
    """
    Form for add/edit catchall account
    """

    action = 'add'
    domain = Domain()
    pwdcharallowed = settings['PWDCHARSALLOWED']
    pwdlengthmin = settings['PWDLENGTHMIN']

    def __init__(self, label='', validators=None, obj=None, action='add', domain=None, *args, **kwargs):
        self.action = action.lower()
        if domain:
            self.domain = domain
        else:
            raise ValueError('No domain object in AccountFormLocal.__init__')

        super().__init__(obj=obj)

        if self.action == 'add':
            del self.submitedit
            self.domain_id = self.domain.domain_id
        elif self.action == 'addpostmaster':
            raise ValueError('Postmaster can not be a catchall account')
        elif self.action == 'edit':
            del self.submitadd
            read_only(self.localpart)
            self.localpart.validators = []

        if self.localpart.data == 'postmaster':
            raise ValueError('Postmaster can not be an catchall account')

    def account_save(self, account):

        if self.validate_on_submit():
            self.populate_obj(account)
            account.domain_id = self.domain.domain_id
            account.pop = path.join(self.domain.maildir, self.localpart.data)
            account.role = settings['ROLE_USER']
            account.type = 'fail'
            account.username = self.localpart.data + '@' + self.domain.domain

            return True
        return False

    localpart = StringField('Localpart', validators=[Length(min=1, max=255)])
    comment = StringField('Comment', validators=[Optional(), Length(min=0, max=255)])
    smtp = TextAreaSepListField('Address', description='', validators=[Length(min=1, max=4096)], separator=', ', render_kw={"rows": 5, "cols": 255})
    submitadd = SubmitField('Add account')
    submitedit = SubmitField('Save account')
    submitcancel = SubmitField('Cancel', render_kw={'formnovalidate': True})
