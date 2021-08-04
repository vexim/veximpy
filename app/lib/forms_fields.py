# app/lib/forms_fields.py
"""
Classes:
  Custom Fields for wtforms
"""

from wtforms.widgets import TextArea
from wtforms import Field


class TextAreaSepListField(Field):
    """
    HTML TextArea rendered field
    Lines will be converted to a with 'separator' separated line for storage 
    Strip spaces
    Strip empty lines
    """

    def __init__(self, label='', validators=None, separator=',', **kwargs):
        super(TextAreaSepListField, self).__init__(label, validators, **kwargs)
        self.separator = separator

    widget = TextArea()

    def _value(self):
        """
        Convert from a semicolon  with 'separator'  string
        to a string with newlines for the HTML-TextArea
        Strip spaces
        Strip empty lines
        """
        if self.data:
            return u'\n'.join([_.strip() for _ in self.data.replace(' ', '').split(self.separator.strip()) if _.strip()])
        else:
            return u''

    def process_formdata(self, valuelist):
        """
        Convert from a with '\n' delimeted string
        to a string delimeted by 'separator' for storage
        Strip spaces
        Strip empty lines
        """
        if valuelist:
            self.data = self.separator.join([_.strip() for _ in valuelist[0].replace(' ', '').splitlines() if _.strip()])
        else:
            self.data = ''
