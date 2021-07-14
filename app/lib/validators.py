# app/lib/validators.py
"""
Functions:
  Validator Functions
"""

import logging
from ..config.settings import settings, domaindefaults

def passwordCheck(password, lengthmin=settings['PWDLENGTHMIN'], charallowed=settings['PWDCHARSALLOWED']):
    """
    Check some rules for passwords
    Password length
    Allowed characters
    """
    val_msg = []
    val_fail = False

    if password is None:
        logging.debug('passwordCheck: No password given.')
        return 'No password given.'
    if len(password) < lengthmin:
        logging.debug('Function PasswordRules. Password too short')
        return 'Password too short. Minimum length is ' + str(lengthmin) + ' characters.'

    if (domaindefaults['pwd_rules'] & settings['PWDRULES_LOWER']):
        val_msg.append('lower case')
        val_fail = val_fail | (not any(_.islower() for _ in password))

    if (domaindefaults['pwd_rules'] & settings['PWDRULES_UPPER']):
        val_msg.append('upper case')
        val_fail = val_fail | (not any(_.isupper() for _ in password))

    if (domaindefaults['pwd_rules'] & settings['PWDRULES_DIGIT']):
        val_msg.append('digits')
        val_fail = val_fail | (not any(_.isdigit() for _ in password))

    if (domaindefaults['pwd_rules'] & settings['PWDRULES_NONALPHA']):
        val_msg.append('special characters')
        val_fail = val_fail | (not any((not _.isalnum() or _ in settings['PWDCHARSLIG']) for _ in password))

    if val_fail:
        logging.debug('Function PasswordRules. Missing char group')
        return 'Password must contain characters of all of following groups: ' + ', '.join(val_msg) + '.'

    if any(not (_ in (charallowed)) for _ in password):
        logging.debug('Function PasswordRules. illegal characters')
        return 'Password contains illegal characters. Allowed characters: ' + charallowed

    return None
