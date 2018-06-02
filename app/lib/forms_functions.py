# app/lib/forms_functions.py
"""
Functions:
  Helper for forms_functions
"""

def bool_checked(value=0):
    """
    Returns the string 'checked' or '' for HTML checkboxes
    Default is '' (=unchecked)
    """
    if value == 1:
        return 'checked'
    return ''
