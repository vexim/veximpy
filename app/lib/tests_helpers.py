# app/lib/tests_helpers.py
# This file is part of veximpy

from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, PasswordField, SelectField, StringField, SubmitField
from app.models.models import Domain
from ..lib.forms_fields import TextAreaSepListField
from ..config.settings import settings

class FormInteger(FlaskForm):
    x = IntegerField('testint')
    quotas = IntegerField('quotas')
    quotasmax = IntegerField('quotasmax')

class FormString(FlaskForm):
    x = StringField('teststring')
    domain_id = StringField('Domain ID')
    localpart = StringField('Localpart')
    
    pwdcharallowed = settings['PWDCHARSALLOWED']
    pwdlengthmin = settings['PWDLENGTHMIN']
    domain = Domain()
    domain.domain = ''


class FormTextAreaSepListField(FlaskForm):
    x = TextAreaSepListField('teststring', separator=' ; ', render_kw={"rows": 5, "cols": 255})
