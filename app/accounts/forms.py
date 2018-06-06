# app/accounts/forms.py
# This file is part of veximpy

from os import path
from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import EqualTo, Length, NumberRange, Optional
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

        super().__init__()
        self.pwdcharallowed = self.domain.pwd_charallowed
        self.pwdlengthmin = self.domain.pwd_lengthmin

        if self.action == 'add':
            if not obj:
                self.set_defaults_from_domain()
            del self.submitedit
            self.domain_id = self.domain.domain_id
        elif self.action == 'addpostmaster':
            self.set_defaults_from_domain()
            self.set_defaults_for_postmaster()
            self.role = postmasterdefaults['role']
        elif self.action == 'edit':
            del self.submitadd
            #form.password1.flags.required = False

        if settings['POSTMASTER_CHANGEUIDGID'] != 1:
            del self.uid
            del self.gid
        if self.localpart.data == 'postmaster':
            del self.enabled
            del self.admin
        if self.domain.pipe != 1:
            del self.on_pipe
            del self.smtp

    def account_save(self, account):
        if self.action == 'add':
            self.password1.flags.required = True
        if self.validate_on_submit():
            self.populate_obj(account)
            account.domain_id = self.domain.domain_id
            if self.username.data == '':
                account.username = self.localpart.data + '@' + self.domain.domain
            if self.password1.data != '':
                account.password_set(self.password1.data)
            account.type = 'local'
            if settings['POSTMASTER_CHANGEUIDGID'] != 1:
                account.uid = self.domain.uid
                account.gid = self.domain.gid
            if self.localpart.data == 'postmaster':
                account.enabled = 1
            if self.domain.pipe != 1:
                account.on_pipe = 0
                account.smtp = path.join(self.domain.maildir, self.localpart.data, 'Maildir')
            account.pop = path.join(self.domain.maildir, self.localpart.data)
            account.role = self.role
            return True
        return False

    def set_defaults_from_domain(self):
        if self.domain.quotas == 0:
            _quotamin = 0
            _quotamax = 2147483647
        else:
            _quotamin = 10
            _quotamax = self.domain.quotas
        self.enabled.data=bool_checked(domaindefaults['enabled'])
        self.realname.data=''
        self.localpart.data=''
        self.username.data=''
        self.comment.data=''
        self.uid.data=self.domain.uid
        self.gid.data=self.domain.gid
        self.admin.data=bool_checked()
        self.on_pipe.data=bool_checked()
        self.smtp.data=self.domain.maildir
        self.quota.data=self.domain.quotas
        self.quota.validators=[NumberRange(min=_quotamin, max=_quotamax)]
        self.maxmsgsize.data=5000
        self.maxmsgsize.validators=[NumberRange(min=1000, max=self.domain.maxmsgsize)]
        self.on_blocklist.data=bool_checked()
        self.on_avscan.data=bool_checked(self.domain.avscan)
        self.on_spamassassin.data=bool_checked(self.domain.spamassassin)
        self.sa_tag.data=self.domain.sa_tag
        self.sa_refuse.data=self.domain.sa_refuse
        self.spam_drop.data=bool_checked()
        self.on_forward.data=bool_checked()
        self.forward.data=''
        self.unseen.data=bool_checked()
        self.on_vacation.data=bool_checked()
        self.vacation.data=''

    def set_defaults_for_postmaster(self):
        self.localpart.data = 'postmaster'
        self.username.data = 'postmaster@' + self.domain.domain
        self.realname.data = 'Postmaster'
        self.uid.data = self.domain.uid
        self.gid.data = self.domain.gid
        self.admin.data =1
        self.on_pipe.data = 0
        self.smtp.data = path.join(self.domain.maildir, 'postmaster', 'Maildir')
        self.quota.data = postmasterdefaults['quota']
        self.maxmsgsize.data = postmasterdefaults['maxmsgsize']
        self.on_blocklist.data = postmasterdefaults['on_blocklist']
        self.on_avscan.data = postmasterdefaults['on_avscan']
        self.on_spamassassin.data = postmasterdefaults['on_spamassassin']
        self.sa_tag.data = postmasterdefaults['sa_tag']
        self.sa_refuse.data = postmasterdefaults['sa_refuse']
        self.spam_drop.data = postmasterdefaults['spam_drop']
        self.on_forward.data = postmasterdefaults['on_forward']
        self.forward.data = postmasterdefaults['forward']
        self.unseen.data = postmasterdefaults['unseen']
        self.on_vacation.data = postmasterdefaults['on_vacation']
        self.vacation.data = postmasterdefaults['vacation']
        self.admin.data = 1


    enabled = BooleanField('Enabled', false_values={0, False, 'false', ''})
    realname = StringField('Realname',
                    description='', validators=[Length(min=1, max=255)])
    localpart = StringField('Localpart',
                    description='', validators=[Localpart, Length(min=1, max=255)])
    username = StringField('Username',
                    description='An arbitrary value. If empty the mailaddress of this account will be used.',
                    validators=[Username, Optional(), Length(min=0, max=255)])
    comment = StringField('Comment', validators=[Optional(), Length(min=0, max=255)])
    password1 = PasswordField('Password', validators=[PasswordRules, EqualTo('password2',
                    message='Password does not match confirmation password.')])
    password2 = PasswordField('Confirm Password')
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
    submitadd = SubmitField('Add domain')
    submitedit = SubmitField('Save domain')
    cancel = SubmitField('Cancel')


class AccountFormAlias(FlaskForm):
    enabled = BooleanField('Enabled', default=bool_checked(domaindefaults['enabled']), false_values={0, False, 'false', ''})
    realname = StringField('Realname', validators=[Length(min=1, max=255)])
    localpart = StringField('Localpart', validators=[Length(min=1, max=255)])
    username = StringField('Username', validators=[Length(min=1, max=255)])
    comment = StringField('Comment', validators=[Optional, Length(min=0, max=255)])
    password_remove = BooleanField('Remove Password. Deny Login.', default=bool_checked(), false_values={0, False, 'false', ''})
    password1 = PasswordField('Password', description='Password only needed if you want the user to be able to log in, or if the Alias is the admin account', validators=[PasswordRules, EqualTo('password2', message='Password does not match confirmation password.')])
    password2 = PasswordField('Confirm Password')
    uid = IntegerField('System UID', default=99, validators=[NumberRange(min=99, max=65535)])
    gid = IntegerField('System GID', default=99, validators=[NumberRange(min=99, max=65535)])
    admin = BooleanField('Domain Admin', default=0, false_values={0, False, 'false', ''})
    smtp = TextAreaSepListField('Address', description='Multiple addresses should be comma separated, with no spaces', validators=[Length(min=1, max=4096)], separator=', ', render_kw={"rows": 5, "cols": 255})
    on_avscan = BooleanField('Anti virus scan', description='Run anti virus scan on mails.', default=1, false_values={0, False, 'false', ''})
    on_spamassassin = BooleanField('Spam check', description='Run spamassassin on mails.', default=1, false_values={0, False, 'false', ''})
    sa_tag = IntegerField('Tag spam above this score', description='Above this score the "X-Spam-Flag: YES" header will be added.', default=3, validators=[NumberRange(min=0, max=99)])
    sa_refuse = IntegerField('Refuse spam above this score', default=5, validators=[NumberRange(min=0, max=99)])
    spam_drop = BooleanField('Move mails above "refuse score" to Junk folder or if disabled delete it.', default=1, false_values={0, False, 'false', ''})
    submitadd = SubmitField('Add domain')
    submitedit = SubmitField('Save domain')
    cancel = SubmitField('Cancel')


class AccountFormFail(FlaskForm):
    enabled = BooleanField('Enabled', default=bool_checked(domaindefaults['enabled']), false_values={0, False, 'false', ''})
    localpart = StringField('Localpart', validators=[Length(min=1, max=255)])
    comment = StringField('Comment', validators=[Optional, Length(min=0, max=255)])
    submitadd = SubmitField('Add domain')
    submitedit = SubmitField('Save domain')
    cancel = SubmitField('Cancel')


class AccountFormMailinglist(FlaskForm):
    submitadd = SubmitField('Add domain')
    submitedit = SubmitField('Save domain')
    cancel = SubmitField('Cancel')


class AccountFormCatchall(FlaskForm):
    localpart = StringField('Localpart', validators=[Length(min=1, max=255)])
    smtp = TextAreaSepListField('Address', description='', validators=[Length(min=1, max=4096)], separator=', ', render_kw={"rows": 5, "cols": 255})
    submitadd = SubmitField('Add domain')
    submitedit = SubmitField('Save domain')
    cancel = SubmitField('Cancel')
